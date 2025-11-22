"""
Extrator de entidades jurídicas usando Gemini (SDK novo) — saída CSV fallback para robustez
"""

import csv
import io
import json
import logging
import re
import time
from typing import Optional, Dict, Tuple

from google import genai
from google.genai.types import GenerateContentConfig

from config import settings, EXTRACTION_PROMPT_PT, EXTRACTION_PROMPT_EN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Cabeçalho CSV fixo (ordem usada no parsing)
CSV_FIELDS = [
    "autor",
    "reu",
    "assunto_principal",
    "tipo_decisao",
    "resultado",
    "resumo_5_linhas",
    "data_decisao",
    "tribunal",
]


class LLMExtractor:
    """Extrator de entidades jurídicas pedindo CSV ao modelo e usando parsing defensivo."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não configurada no .env")

        # Cliente stateful do SDK novo
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = settings.MODEL_NAME

        logger.info(f"LLM Extractor inicializado com modelo: {self.model_name}")

    # -------------------------
    # Prompt builder (CSV)
    # -------------------------
    def _build_csv_prompt(self, text: str, language: str = "pt") -> str:
        """
        Gera um prompt que pede uma linha CSV com cabeçalho fixo.
        Instrui o modelo a:
          - produzir exatamente o cabeçalho (uma linha) e uma linha de valores
          - substituir quebras de linha em resumo por a sequência literal '\n'
          - usar aspas para campos que contiverem vírgulas
        """
        base_prompt = EXTRACTION_PROMPT_PT if language == "pt" else EXTRACTION_PROMPT_EN

        csv_instruction = f"""
AGORA: Produza EXATAMENTE DUAS LINHAS CSV: a primeira deve ser o cabeçalho
com estas colunas, nesta ordem:

{', '.join(CSV_FIELDS)}

A segunda linha deve conter os valores correspondentes. Regras importantes:
- Não escreva texto adicional além das duas linhas CSV.
- Se um campo contiver quebras de linha (por exemplo o resumo), substitua cada quebra por a sequência de dois caracteres '\\n' (barra invertida + n).
- Se um campo contiver vírgulas, coloque-o entre aspas (padrão CSV).
- Se não for possível extrair um campo, deixe-o vazio (i.e. ,,).
- Temperatura 0: seja factual e conciso.

Agora produza as 2 linhas (cabeçalho + valores) para o texto do documento abaixo.
DOCUMENTO:
{text}
"""
        # Não usar .format para evitar colisões com {{document_text}} do template original.
        # Retornamos a instrução + o texto (não precisamos do template original para o CSV)
        return csv_instruction.strip()

    # -------------------------
    # Chamada ao modelo e parsing
    # -------------------------
    def extract_entities(
        self,
        text: str,
        language: str = "pt",
        retry: bool = True
    ) -> Optional[Dict[str, Optional[str]]]:
        """
        Tenta extrair entidades retornando um dict. Usa CSV como formato intermediário.
        Em caso de falha no CSV, tenta fallback heurístico.
        """
        prompt = self._build_csv_prompt(text, language)
        attempts = settings.MAX_RETRIES if retry else 1

        for attempt in range(1, attempts + 1):
            try:
                logger.info(f"Tentativa {attempt}/{attempts} de extração (CSV)")

                config = GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=settings.MAX_TOKENS,
                )

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt],
                    config=config,
                )

                # prefer parsed text if disponível, senão use response.text
                raw_text = ""
                if hasattr(response, "text") and response.text:
                    raw_text = response.text
                elif hasattr(response, "candidates") and response.candidates:
                    # pega concatenação das parts se existirem
                    try:
                        parts = response.candidates[0].content.parts
                        raw_text = "".join(getattr(p, "text", "") for p in parts)
                    except Exception:
                        raw_text = str(response.candidates[0])
                elif hasattr(response, "parsed") and response.parsed:
                    # caso raro: response.parsed já seja um dict -> convertemos para CSV-like (incomum)
                    parsed = response.parsed
                    logger.debug("Resposta já parseada pelo cliente (parsed). Converto para dict.")
                    return {k: parsed.get(k) for k in CSV_FIELDS}

                raw_text = raw_text.strip()
                logger.debug(f"RAW MODEL OUTPUT:\n{raw_text}")

                # Tentativa 1: parse CSV padrão
                parsed = self._parse_csv_output(raw_text)
                if parsed:
                    return parsed

                # Tentativa 2: extrair CSV embutido (ex.: modelo colocou texto antes/depois)
                embedded = self._extract_csv_block(raw_text)
                if embedded:
                    parsed2 = self._parse_csv_output(embedded)
                    if parsed2:
                        return parsed2

                # Tentativa 3: fallback por extração por labels (regex heurístico)
                logger.warning("CSV inválido — tentando fallback heurístico por rótulos")
                heuristic = self._heuristic_extract(text)
                if heuristic:
                    return heuristic

                logger.warning("Falha ao extrair entidades (nenhum método funcionou)")

            except Exception as e:
                logger.error(f"Erro na tentativa {attempt}: {e}")

            # backoff exponencial simples
            if attempt < attempts:
                time.sleep(2 ** (attempt - 1))

        return None

    # -------------------------
    # CSV parsing helpers
    # -------------------------
    def _parse_csv_output(self, raw: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Tenta parsear duas linhas CSV (header + values) ou uma linha com apenas values.
        Retorna dict com chaves CSV_FIELDS.
        """
        if not raw:
            return None

        # Normaliza possíveis CRLF
        raw = raw.replace("\r\n", "\n").strip()

        # Se o modelo retornou o cabeçalho + linha de dados, tudo certo.
        lines = [ln for ln in raw.split("\n") if ln.strip() != ""]
        if len(lines) >= 2:
            header_line = lines[0].strip()
            data_line = "\n".join(lines[1:]).strip()  # junta caso resumo contenha quebras transformadas em \n
        elif len(lines) == 1:
            # Só uma linha: assumimos que é a linha de valores (sem cabeçalho)
            header_line = ",".join(CSV_FIELDS)
            data_line = lines[0].strip()
        else:
            return None

        # Use csv.reader para respeitar aspas
        try:
            f = io.StringIO(f"{header_line}\n{data_line}\n")
            reader = csv.DictReader(f)
            row = next(reader, None)
            if not row:
                return None

            # Normalize: transformar '' em None e substituir '\n' por nova linha literal se desejar
            normalized = {}
            for k in CSV_FIELDS:
                v = row.get(k)
                if v is None:
                    normalized[k] = None
                else:
                    v = v.strip()
                    # restaurar quebras: modelo foi instruído a usar '\\n' para novas linhas
                    v = v.replace("\\n", "\n")
                    normalized[k] = v if v != "" else None

            return normalized
        except Exception as e:
            logger.debug(f"Erro ao parsear CSV com csv.DictReader: {e}")
            return None

    def _extract_csv_block(self, text: str) -> Optional[str]:
        """
        Extrai blocos que pareçam CSV (linhas contendo vírgulas e aspas) dentro de texto maior.
        Retorna o bloco CSV (header+values) ou None.
        """
        # procura por linhas com muitas vírgulas (heurística)
        candidate_lines = [ln for ln in text.splitlines() if ln.count(",") >= 3]
        if not candidate_lines:
            return None

        # tenta juntar duas linhas consecutivas candidatas
        for i in range(len(candidate_lines) - 1):
            block = candidate_lines[i] + "\n" + candidate_lines[i + 1]
            # verifica se contém o cabeçalho esperado ou tem tamanho de colunas compatível
            if all(field in block or field in candidate_lines[i] for field in CSV_FIELDS[:3]):
                return block

        # fallback: retorna as duas primeiras linhas candidatas
        if len(candidate_lines) >= 2:
            return candidate_lines[0] + "\n" + candidate_lines[1]

        return None

    # -------------------------
    # Heurística fallback por rótulos
    # -------------------------
    def _heuristic_extract(self, text: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Heurística simples: busca padrões comuns no texto para extrair campos.
        Não é perfeita, é fallback.
        """
        # Normaliza espaços
        t = re.sub(r"\s+", " ", text)

        def find_after(key_patterns):
            for pat in key_patterns:
                m = re.search(rf"{pat}\s*[:\-–]\s*(.+?)(?=\s+[A-Z][a-z]+:|\Z)", t, flags=re.IGNORECASE)
                if m:
                    return m.group(1).strip()
            return None

        # padrões típicos
        autor = find_after([r"^(appellant|petitioner|plaintiff|autor|peticioner|petitioner)", r"(?<=versus\s).*?(?=\s+v\b)"])
        reu = find_after([r"defendant|respondent|respondent:|réu|respondente", r"versus\s+(.+?)\s"])
        assunto = find_after([r"subject|assunto|matter|case about|challenge to|challenge of"])
        tipo = find_after([r"judgment|order|decision|sentença|acórdão|order:"])
        resultado = find_after([r"result|disposition|held that|decided that|order|disposed", r"result:"])
        data = None
        mdate = re.search(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text)
        if mdate:
            data = mdate.group(1)
        tribunal = find_after([r"court|tribunal|supreme court|tribunal de", r"in the (supreme court|high court)"])

        # monta dicionário
        out = {
            "autor": autor,
            "reu": reu,
            "assunto_principal": assunto,
            "tipo_decisao": tipo,
            "resultado": resultado,
            "resumo_5_linhas": None,
            "data_decisao": data,
            "tribunal": tribunal,
        }

        # Se nenhuma informação útil encontrada, retorna None
        if not any(out.values()):
            return None

        return out

    # -------------------------
    # Conveniência: retornar CSV string também
    # -------------------------
    def dict_to_csv_line(self, d: Dict[str, Optional[str]]) -> str:
        """
        Converte dict em linha CSV (apenas os valores, sem cabeçalho).
        Usa csv.writer para escapar corretamente.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        row = []
        for f in CSV_FIELDS:
            v = d.get(f)
            # substitui novas linhas por sequência literal '\n'
            if v is None:
                row.append("")
            else:
                row.append(v.replace("\n", "\\n"))
        writer.writerow(row)
        return output.getvalue().strip()
