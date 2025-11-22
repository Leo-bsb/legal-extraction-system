"""
Módulo para cálculo de métricas de avaliação
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExtractionMetrics:
    """Métricas de extração"""
    total_documents: int
    successful_extractions: int
    failed_extractions: int
    success_rate: float
    avg_completeness: float
    avg_extraction_time: float
    field_extraction_rates: Dict[str, float]
    error_types: Dict[str, int]


class MetricsCalculator:
    """Calcula métricas de desempenho do sistema"""
    
    def __init__(self):
        self.extractions = []
        self.validation_results = []
        self.processing_times = []
    
    def add_extraction(self, filename: str, entities: Optional[Dict], 
                      completeness: float, processing_time: float,
                      success: bool, errors: Optional[List[str]] = None):
        """
        Adiciona resultado de extração
        
        Args:
            filename: Nome do arquivo
            entities: Entidades extraídas
            completeness: Score de completude
            processing_time: Tempo de processamento
            success: Se foi bem-sucedido
            errors: Lista de erros
        """
        self.extractions.append({
            'filename': filename,
            'entities': entities,
            'completeness': completeness,
            'processing_time': processing_time,
            'success': success,
            'errors': errors or []
        })
    
    def calculate_metrics(self) -> ExtractionMetrics:
        """
        Calcula todas as métricas
        
        Returns:
            Objeto com métricas calculadas
        """
        if not self.extractions:
            logger.warning("Nenhuma extração para calcular métricas")
            return ExtractionMetrics(
                total_documents=0,
                successful_extractions=0,
                failed_extractions=0,
                success_rate=0.0,
                avg_completeness=0.0,
                avg_extraction_time=0.0,
                field_extraction_rates={},
                error_types={}
            )
        
        total = len(self.extractions)
        successful = sum(1 for e in self.extractions if e['success'])
        failed = total - successful
        
        success_rate = successful / total if total > 0 else 0.0
        
        # Completude média
        completeness_scores = [e['completeness'] for e in self.extractions if e['completeness'] is not None]
        avg_completeness = statistics.mean(completeness_scores) if completeness_scores else 0.0
        
        # Tempo médio
        times = [e['processing_time'] for e in self.extractions if e['processing_time'] is not None]
        avg_time = statistics.mean(times) if times else 0.0
        
        # Taxa de extração por campo
        field_rates = self._calculate_field_rates()
        
        # Tipos de erros
        error_types = self._calculate_error_types()
        
        metrics = ExtractionMetrics(
            total_documents=total,
            successful_extractions=successful,
            failed_extractions=failed,
            success_rate=success_rate,
            avg_completeness=avg_completeness,
            avg_extraction_time=avg_time,
            field_extraction_rates=field_rates,
            error_types=error_types
        )
        
        logger.info(f"Métricas calculadas: Success Rate = {success_rate:.2%}")
        return metrics
    
    def _calculate_field_rates(self) -> Dict[str, float]:
        """
        Calcula taxa de sucesso por campo
        
        Returns:
            Dicionário {campo: taxa}
        """
        field_counts = {}
        total_extractions = 0
        
        for extraction in self.extractions:
            if not extraction['success'] or not extraction['entities']:
                continue
            
            total_extractions += 1
            entities = extraction['entities']
            
            for field, value in entities.items():
                if value and str(value).lower() not in ['null', 'none', 'n/a', '']:
                    field_counts[field] = field_counts.get(field, 0) + 1
        
        if total_extractions == 0:
            return {}
        
        return {
            field: count / total_extractions 
            for field, count in field_counts.items()
        }
    
    def _calculate_error_types(self) -> Dict[str, int]:
        """
        Conta tipos de erros
        
        Returns:
            Dicionário {tipo_erro: contagem}
        """
        error_types = {}
        
        for extraction in self.extractions:
            if extraction['errors']:
                for error in extraction['errors']:
                    # Extrai tipo do erro (primeira palavra)
                    error_type = error.split(':')[0].strip() if ':' in error else 'unknown'
                    error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return error_types
    
    def generate_report(self) -> str:
        """
        Gera relatório textual das métricas
        
        Returns:
            String com relatório formatado
        """
        metrics = self.calculate_metrics()
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║           RELATÓRIO DE MÉTRICAS DE EXTRAÇÃO             ║
╚══════════════════════════════════════════════════════════╝

📊 RESUMO GERAL
  • Total de Documentos: {metrics.total_documents}
  • Extrações Bem-sucedidas: {metrics.successful_extractions}
  • Extrações Falhadas: {metrics.failed_extractions}
  • Taxa de Sucesso: {metrics.success_rate:.2%}

📈 QUALIDADE DA EXTRAÇÃO
  • Completude Média: {metrics.avg_completeness:.2%}
  • Tempo Médio de Processamento: {metrics.avg_extraction_time:.2f}s

🎯 TAXA DE EXTRAÇÃO POR CAMPO
"""
        
        for field, rate in sorted(metrics.field_extraction_rates.items(), 
                                 key=lambda x: x[1], reverse=True):
            bar_length = int(rate * 30)
            bar = '█' * bar_length + '░' * (30 - bar_length)
            report += f"  • {field:20s} [{bar}] {rate:.1%}\n"
        
        if metrics.error_types:
            report += "\n⚠️  TIPOS DE ERROS\n"
            for error_type, count in sorted(metrics.error_types.items(), 
                                           key=lambda x: x[1], reverse=True):
                report += f"  • {error_type}: {count} ocorrências\n"
        
        report += "\n" + "="*60
        
        return report
    
    def get_performance_summary(self) -> Dict:
        """
        Retorna resumo de performance para dashboard
        
        Returns:
            Dicionário com métricas resumidas
        """
        metrics = self.calculate_metrics()
        
        return {
            'total_documents': metrics.total_documents,
            'success_rate': round(metrics.success_rate * 100, 2),
            'avg_completeness': round(metrics.avg_completeness * 100, 2),
            'avg_time': round(metrics.avg_extraction_time, 2),
            'field_rates': {
                k: round(v * 100, 2) 
                for k, v in metrics.field_extraction_rates.items()
            }
        }
    
    def compare_with_ground_truth(self, ground_truth: Dict[str, Dict]) -> Dict[str, float]:
        """
        Compara extrações com ground truth (quando disponível)
        
        Args:
            ground_truth: Dicionário {filename: entities_corretas}
            
        Returns:
            Dicionário com métricas de precisão
        """
        if not ground_truth:
            logger.warning("Ground truth não fornecido")
            return {}
        
        precision_scores = []
        recall_scores = []
        
        for extraction in self.extractions:
            filename = extraction['filename']
            
            if filename not in ground_truth or not extraction['success']:
                continue
            
            extracted = extraction['entities']
            truth = ground_truth[filename]
            
            # Calcula precisão e recall por campo
            correct = 0
            total_extracted = 0
            total_truth = 0
            
            for field in truth.keys():
                truth_value = truth.get(field)
                extracted_value = extracted.get(field)
                
                if truth_value:
                    total_truth += 1
                
                if extracted_value:
                    total_extracted += 1
                    
                    # Verifica se está correto (comparação simples)
                    if str(extracted_value).lower().strip() == str(truth_value).lower().strip():
                        correct += 1
            
            if total_extracted > 0:
                precision = correct / total_extracted
                precision_scores.append(precision)
            
            if total_truth > 0:
                recall = correct / total_truth
                recall_scores.append(recall)
        
        avg_precision = statistics.mean(precision_scores) if precision_scores else 0.0
        avg_recall = statistics.mean(recall_scores) if recall_scores else 0.0
        
        f1_score = 0.0
        if avg_precision + avg_recall > 0:
            f1_score = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)
        
        return {
            'precision': avg_precision,
            'recall': avg_recall,
            'f1_score': f1_score
        }