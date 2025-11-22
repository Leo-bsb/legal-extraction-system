"""
Script Principal para Processamento em Lote de PDFs Jurídicos
"""
import argparse
import logging
from pathlib import Path
from typing import Optional
import time
from tqdm import tqdm

from src.pdf_processor import PDFProcessor
from src.text_cleaner import TextCleaner
from src.llm_extractor import LLMExtractor
from src.validator import EntityValidator
from src.database import Database
from src.metrics import MetricsCalculator
from src.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LegalExtractionPipeline:
    """Pipeline completo de extração"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.text_cleaner = TextCleaner()
        self.validator = EntityValidator()
        self.db = Database()
        self.metrics_calc = MetricsCalculator()
        
        # LLM é inicializada por processamento (evita problemas de API)
        self.llm_extractor = None
    
    def _init_llm(self):
        """Inicializa LLM extractor"""
        if not self.llm_extractor:
            try:
                self.llm_extractor = LLMExtractor()
                logger.info("LLM Extractor inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar LLM: {e}")
                raise
    
    def process_single_pdf(self, pdf_path: Path, language: str = 'en') -> bool:
        """
        Processa um único PDF
        
        Args:
            pdf_path: Caminho para o PDF
            language: Idioma ('pt' ou 'en')
            
        Returns:
            True se sucesso
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processando: {pdf_path.name}")
            
            # 1. Extrai texto
            text = self.pdf_processor.extract_text(pdf_path)
            
            if not text:
                logger.warning(f"Texto vazio: {pdf_path.name}")
                self.metrics_calc.add_extraction(
                    filename=pdf_path.name,
                    entities=None,
                    completeness=0.0,
                    processing_time=time.time() - start_time,
                    success=False,
                    errors=["Texto vazio"]
                )
                return False
            
            # 2. Limpa texto
            clean_text = self.text_cleaner.clean(text)
            
            # Detecta idioma se necessário
            if language == 'auto':
                language = self.pdf_processor.detect_language(clean_text)
                logger.info(f"Idioma detectado: {language}")
            
            # Trunca texto
            truncated_text = self.text_cleaner.truncate_for_llm(clean_text)
            
            # 3. Extrai entidades
            self._init_llm()
            
            entities = self.llm_extractor.extract_entities(truncated_text, language)
            
            if not entities:
                logger.warning(f"Falha na extração: {pdf_path.name}")
                self.metrics_calc.add_extraction(
                    filename=pdf_path.name,
                    entities=None,
                    completeness=0.0,
                    processing_time=time.time() - start_time,
                    success=False,
                    errors=["Falha na extração"]
                )
                return False
            
            # 4. Valida
            is_valid, validated_entities, errors = self.validator.validate(entities)
            completeness = self.validator.calculate_completeness(validated_entities)
            
            # 5. Salva no banco
            metadata = self.pdf_processor.get_metadata(pdf_path)
            
            self.db.insert_case(
                filename=pdf_path.name,
                entities=validated_entities,
                language=language,
                year=metadata.year,
                completeness_score=completeness,
                validation_errors=errors
            )
            
            # Métricas
            processing_time = time.time() - start_time
            
            self.db.insert_metric(
                filename=pdf_path.name,
                extraction_time=processing_time,
                num_retries=1,
                success=True
            )
            
            self.metrics_calc.add_extraction(
                filename=pdf_path.name,
                entities=validated_entities,
                completeness=completeness,
                processing_time=processing_time,
                success=True,
                errors=errors
            )
            
            logger.info(f"✓ Processado em {processing_time:.2f}s - Completude: {completeness:.1%}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar {pdf_path.name}: {e}")
            
            processing_time = time.time() - start_time
            self.metrics_calc.add_extraction(
                filename=pdf_path.name,
                entities=None,
                completeness=0.0,
                processing_time=processing_time,
                success=False,
                errors=[str(e)]
            )
            
            return False
    
    def process_directory(
        self, 
        directory: Path, 
        language: str = 'en',
        max_files: Optional[int] = None,
        recursive: bool = False
    ):
        """
        Processa todos os PDFs de um diretório
        
        Args:
            directory: Diretório com PDFs
            language: Idioma dos documentos
            max_files: Limite de arquivos (None = todos)
            recursive: Se deve buscar em subdiretórios
        """
        logger.info(f"Buscando PDFs em: {directory}")
        
        # Encontra PDFs
        if recursive:
            pdf_files = list(directory.rglob("*.pdf"))
        else:
            pdf_files = list(directory.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning("Nenhum PDF encontrado")
            return
        
        if max_files:
            pdf_files = pdf_files[:max_files]
        
        logger.info(f"Encontrados {len(pdf_files)} PDFs")
        
        # Processa com barra de progresso
        successful = 0
        failed = 0
        
        for pdf_path in tqdm(pdf_files, desc="Processando PDFs"):
            success = self.process_single_pdf(pdf_path, language)
            
            if success:
                successful += 1
            else:
                failed += 1
            
            # Rate limiting
            time.sleep(1)
        
        logger.info(f"\n✓ Sucesso: {successful} | ✗ Falhas: {failed}")
        
        # Relatório de métricas
        print("\n" + "="*60)
        print(self.metrics_calc.generate_report())
        print("="*60)


def main():
    """Função principal"""
    
    parser = argparse.ArgumentParser(
        description="Sistema de Extração de Informações Jurídicas com LLM"
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Caminho para PDF ou diretório com PDFs'
    )
    
    parser.add_argument(
        '--language',
        type=str,
        default='auto',
        choices=['auto', 'pt', 'en'],
        help='Idioma dos documentos (padrão: auto)'
    )
    
    parser.add_argument(
        '--max-files',
        type=int,
        default=None,
        help='Número máximo de arquivos a processar'
    )
    
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Buscar PDFs recursivamente em subdiretórios'
    )
    
    parser.add_argument(
        '--export-csv',
        type=str,
        default=None,
        help='Caminho para exportar resultados em CSV'
    )
    
    args = parser.parse_args()
    
    # Verifica API key
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY não configurada!")
        logger.error("Configure a chave no arquivo .env")
        return
    
    # Inicializa pipeline
    pipeline = LegalExtractionPipeline()
    
    input_path = Path(args.input)
    
    # Processa
    if input_path.is_file():
        # PDF único
        pipeline.process_single_pdf(input_path, args.language)
    elif input_path.is_dir():
        # Diretório
        pipeline.process_directory(
            input_path,
            args.language,
            args.max_files,
            args.recursive
        )
    else:
        logger.error(f"Caminho inválido: {input_path}")
        return
    
    # Exporta CSV se solicitado
    if args.export_csv:
        export_path = Path(args.export_csv)
        if pipeline.db.export_to_csv(export_path):
            logger.info(f"✓ Dados exportados para: {export_path}")
    
    # Fecha banco
    pipeline.db.close()
    
    logger.info("✓ Processamento concluído!")


if __name__ == "__main__":
    main()