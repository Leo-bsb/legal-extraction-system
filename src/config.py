import os
from pathlib import Path
from typing import Tuple
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


# =======================
#   SETTINGS CLASS
# =======================
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",      # evitar crashes por variáveis extras
    )

    # ======================
    #   ENV VARS
    # ======================
    GEMINI_API_KEY: str

    # ======================
    #   PATHS
    # ======================
    BASE_DIR: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent
    )

    DATA_ROOT: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data")
    RAW_DATA: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "raw")
    PROCESSED_DATA: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "processed")
    RESULTS: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "results")
    LOGS: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "logs")

    # ======================
    #   MODEL CONFIG
    # ======================
    MODEL_NAME: str = "gemini-2.5-flash"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.0

    # ======================
    #   PROCESSING
    # ======================
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 50
    MAX_RETRIES: int = 5

    ENTITIES: Tuple[str, ...] = (
        "autor",
        "reu",
        "assunto_principal",
        "tipo_decisao",
        "resultado",
        "resumo_5_linhas",
        "data_decisao",
        "tribunal",
    )

    VALID_RESULTS: Tuple[str, ...] = (
        "granted", "denied", "dismissed", "allowed",
        "rejected", "deferido", "indeferido",
        "procedente", "improcedente", "arquivado",
    )

    MIN_SUMMARY_LINES: int = 1
    MAX_SUMMARY_LINES: int = 5

    # ======================
    #   API CONFIG
    # ======================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ======================
    #   DB
    # ======================
    DB_PATH: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "legal_cases.db")

    def setup_directories(self):
        for path in [self.RAW_DATA, self.PROCESSED_DATA, self.RESULTS, self.LOGS]:
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.setup_directories()


# ======================
#   PROMPTS
# ======================

EXTRACTION_PROMPT_PT = """
Você é um sistema especializado em extração estruturada de informações de decisões judiciais.

Sua tarefa: ler o texto a seguir e produzir **apenas uma única linha CSV**, com todos os campos abaixo preenchidos em **português**, mesmo que o documento esteja em inglês.

ORDEM EXATA DAS COLUNAS:
autor, reu, assunto_principal, tipo_decisao, resultado, resumo_5_linhas, data_decisao, tribunal

REGRAS IMPORTANTES:
1. Retorne **somente CSV**, sem texto antes ou depois.
2. Se um campo não estiver claro no texto, produza **sua melhor inferência explícita**, nunca deixe vazio.
3. O campo **resultado** DEVE ser um dos seguintes rótulos:
   [deferido, indeferido, procedente, improcedente, arquivado,
    granted, denied, dismissed, allowed, rejected]
4. O campo **resumo_5_linhas** deve conter no máximo 5 linhas, em português.
5. O campo **data_decisao** deve ser obrigatoriamente obrigatoriamente convertido para o formato **DD/MM/AAAA**, mesmo que o texto esteja em outro formato.
6. O campo **tipo_decisao** deve ser traduzido para português (ex: ORDER → Ordem; JUDGMENT → Julgamento).
7. O output deve usar vírgulas como separador e aspas para campos com vírgulas internas.

Texto analisado:
{{document_text}}




Agora produza exclusivamente:

autor,reu,assunto_principal,tipo_decisao,resultado,resumo_5_linhas,data_decisao,tribunal
"""

EXTRACTION_PROMPT_EN = """
You are an expert in judicial decision analysis.

Extract specific information from the provided document and return ONLY
a single CSV line with the following fixed header:

autor,reu,assunto_principal,tipo_decisao,resultado,resumo_5_linhas,data_decisao,tribunal

Important rules:
- The output must contain exactly 1 data row.
- Replace internal commas with semicolons (;).
- Field "resultado" MUST be one of:
  [granted, denied, dismissed, allowed, rejected,
   deferido, indeferido, procedente, improcedente, arquivado]
- The summary must contain at most 5 lines, merged using semicolons instead of line breaks.
- Do not add anything outside the CSV.
- No comments, no explanations.

Document text:
{{document_text}}

Now produce only:

autor,reu,assunto_principal,tipo_decisao,resultado,resumo_5_linhas,data_decisao,tribunal
"""
