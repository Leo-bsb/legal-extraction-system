"""
Módulo para limpeza e normalização de texto
"""
import re
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextCleaner:
    """Limpa e normaliza texto extraído de PDFs"""
    
    def __init__(self):
        # Padrões de cabeçalhos repetitivos comuns
        self.header_patterns = [
            r'Page \d+ of \d+',
            r'www\.\S+',
            r'©\s*\d{4}',
            r'All Rights Reserved',
        ]
    
    def clean(self, text: str) -> str:
        """
        Pipeline completo de limpeza
        
        Args:
            text: Texto bruto
            
        Returns:
            Texto limpo
        """
        if not text:
            return ""
        
        text = self._remove_headers(text)
        text = self._normalize_whitespace(text)
        text = self._fix_line_breaks(text)
        text = self._remove_special_chars(text)
        
        return text.strip()
    
    def _remove_headers(self, text: str) -> str:
        """Remove cabeçalhos e rodapés repetitivos"""
        for pattern in self.header_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normaliza espaços em branco"""
        # Remove espaços múltiplos
        text = re.sub(r' +', ' ', text)
        # Remove tabs
        text = text.replace('\t', ' ')
        return text
    
    def _fix_line_breaks(self, text: str) -> str:
        """Corrige quebras de linha"""
        # Remove quebras de linha no meio de frases
        text = re.sub(r'(?<=[a-z,])\n(?=[a-z])', ' ', text)
        # Normaliza múltiplas quebras
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text
    
    def _remove_special_chars(self, text: str) -> str:
        """Remove caracteres especiais problemáticos"""
        # Remove caracteres de controle (exceto \n)
        text = ''.join(char for char in text if char == '\n' or not char.isspace() or char == ' ')
        # Remove marcadores de PDF
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        return text
    
    def extract_sections(self, text: str) -> dict:
        """
        Extrai seções comuns de documentos jurídicos
        
        Args:
            text: Texto do documento
            
        Returns:
            Dicionário com seções identificadas
        """
        sections = {
            'header': '',
            'facts': '',
            'arguments': '',
            'decision': '',
            'full_text': text
        }
        
        # Padrões para identificar seções (português e inglês)
        patterns = {
            'facts': r'(?:FACTS?|FATOS|RELAT[ÓO]RIO).*?(?=\n\n)',
            'arguments': r'(?:ARGUMENTS?|ARGUMENTOS|FUNDAMENTOS?).*?(?=\n\n)',
            'decision': r'(?:DECISION|DECIS[ÃA]O|CONCLUS[ÃA]O|DISPOSITIVO).*',
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section] = match.group(0)
        
        return sections
    
    def truncate_for_llm(self, text: str, max_tokens: int = 7000) -> str:
        """
        Trunca texto para caber no limite de tokens da LLM
        Aproximação: 1 token ≈ 4 caracteres
        
        Args:
            text: Texto completo
            max_tokens: Máximo de tokens
            
        Returns:
            Texto truncado
        """
        max_chars = max_tokens * 4
        
        if len(text) <= max_chars:
            return text
        
        # Tenta manter seções importantes
        sections = self.extract_sections(text)
        
        # Prioriza: header + decision + facts
        priority_text = (
            sections.get('header', '')[:500] + '\n\n' +
            sections.get('decision', '')[:2000] + '\n\n' +
            sections.get('facts', '')[:2000]
        )
        
        if len(priority_text) > max_chars:
            return priority_text[:max_chars]
        
        # Adiciona o resto até o limite
        remaining = max_chars - len(priority_text)
        full_text = sections['full_text']
        
        return priority_text + '\n\n' + full_text[:remaining]


class TextChunker:
    """Divide texto em chunks para processamento"""
    
    def __init__(self, chunk_size: int = 3000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Divide texto em chunks com overlap
        
        Args:
            text: Texto completo
            
        Returns:
            Lista de chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Tenta quebrar em final de sentença
            if end < len(text):
                # Procura por ponto final próximo
                sentence_end = text.rfind('.', start, end)
                if sentence_end != -1 and sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
            
            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap
        
        logger.info(f"Texto dividido em {len(chunks)} chunks")
        return chunks