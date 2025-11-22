"""
Módulo para extração de texto de PDFs
"""
import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PDFMetadata:
    """Metadados de um PDF"""
    filename: str
    num_pages: int
    file_size: int
    year: Optional[str] = None


class PDFProcessor:
    """Processa PDFs e extrai texto"""
    
    def __init__(self):
        self.encoding = 'utf-8'
    
    def extract_text(self, pdf_path: Path) -> Optional[str]:
        """
        Extrai texto de um PDF
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Texto extraído ou None em caso de erro
        """
        try:
            doc = fitz.open(pdf_path)
            text_parts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
            
            doc.close()
            
            full_text = "\n\n".join(text_parts)
            
            if not full_text.strip():
                logger.warning(f"PDF vazio ou sem texto extraível: {pdf_path}")
                return None
            
            logger.info(f"Texto extraído com sucesso: {pdf_path.name} ({len(full_text)} chars)")
            return full_text
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto de {pdf_path}: {e}")
            return None
    
    def get_metadata(self, pdf_path: Path) -> PDFMetadata:
        """
        Extrai metadados do PDF
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Metadados do PDF
        """
        try:
            doc = fitz.open(pdf_path)
            num_pages = len(doc)
            doc.close()
            
            file_size = pdf_path.stat().st_size
            year = self._extract_year_from_path(pdf_path)
            
            return PDFMetadata(
                filename=pdf_path.name,
                num_pages=num_pages,
                file_size=file_size,
                year=year
            )
        except Exception as e:
            logger.error(f"Erro ao extrair metadados de {pdf_path}: {e}")
            return PDFMetadata(
                filename=pdf_path.name,
                num_pages=0,
                file_size=0
            )
    
    def _extract_year_from_path(self, pdf_path: Path) -> Optional[str]:
        """
        Extrai o ano do caminho do arquivo
        
        Args:
            pdf_path: Caminho do PDF
            
        Returns:
            Ano como string ou None
        """
        parts = pdf_path.parts
        for part in parts:
            if part.isdigit() and 1950 <= int(part) <= 2025:
                return part
        return None
    
    def process_batch(self, pdf_paths: list[Path]) -> Dict[str, str]:
        """
        Processa múltiplos PDFs
        
        Args:
            pdf_paths: Lista de caminhos para PDFs
            
        Returns:
            Dicionário {filename: texto_extraído}
        """
        results = {}
        
        for pdf_path in pdf_paths:
            text = self.extract_text(pdf_path)
            if text:
                results[pdf_path.name] = text
        
        logger.info(f"Processados {len(results)}/{len(pdf_paths)} PDFs com sucesso")
        return results
    
    def detect_language(self, text: str) -> str:
        """
        Detecta o idioma do texto (simplificado)
        
        Args:
            text: Texto a analisar
            
        Returns:
            'pt' ou 'en'
        """
        # Palavras comuns em português jurídico
        pt_keywords = ['autor', 'réu', 'processo', 'sentença', 'acórdão', 
                       'tribunal', 'recurso', 'decisão']
        
        # Palavras comuns em inglês jurídico
        en_keywords = ['plaintiff', 'defendant', 'court', 'judgment', 
                       'appeal', 'order', 'petition']
        
        text_lower = text.lower()[:5000]  # Analisa apenas início
        
        pt_count = sum(1 for word in pt_keywords if word in text_lower)
        en_count = sum(1 for word in en_keywords if word in text_lower)
        
        return 'pt' if pt_count > en_count else 'en'


# Função auxiliar para uso direto
def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Função auxiliar para extração rápida de texto
    
    Args:
        pdf_path: Caminho do arquivo PDF
        
    Returns:
        Texto extraído
    """
    processor = PDFProcessor()
    return processor.extract_text(Path(pdf_path))