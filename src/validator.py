"""
Módulo para validação de entidades extraídas
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EntityValidator:
    """Valida e normaliza entidades extraídas"""
    
    def __init__(self):
        self.valid_results = [r.lower() for r in settings.VALID_RESULTS]
    
    def validate(self, entities: Dict) -> Tuple[bool, Dict, List[str]]:
        """
        Valida todas as entidades
        
        Args:
            entities: Dicionário de entidades
            
        Returns:
            (is_valid, validated_entities, errors)
        """
        errors = []
        validated = entities.copy()
        
        # Valida cada campo
        validators = {
            'autor': self._validate_party_name,
            'reu': self._validate_party_name,
            'assunto_principal': self._validate_subject,
            'tipo_decisao': self._validate_decision_type,
            'resultado': self._validate_result,
            'resumo_5_linhas': self._validate_summary,
            'data_decisao': self._validate_date,
            'tribunal': self._validate_court,
        }
        
        for field, validator in validators.items():
            if field in validated:
                is_valid, normalized_value, error = validator(validated[field])
                
                if not is_valid:
                    errors.append(f"{field}: {error}")
                
                validated[field] = normalized_value
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.warning(f"Validação falhou: {errors}")
        else:
            logger.info("Validação bem-sucedida")
        
        return is_valid, validated, errors
    
    def _validate_party_name(self, value: str) -> Tuple[bool, Optional[str], str]:
        """Valida nome de parte"""
        if not value or value.lower() in ['null', 'none', 'n/a']:
            return True, None, ""
        
        # Remove espaços extras
        normalized = ' '.join(value.split())
        
        # Verifica se tem pelo menos 2 caracteres
        if len(normalized) < 2:
            return False, None, "Nome muito curto"
        
        # Verifica se não é apenas números
        if normalized.replace(' ', '').isdigit():
            return False, None, "Nome não pode ser apenas números"
        
        return True, normalized, ""
    
    def _validate_subject(self, value: str) -> Tuple[bool, Optional[str], str]:
        """Valida assunto principal"""
        if not value or value.lower() in ['null', 'none', 'n/a']:
            return True, None, ""
        
        normalized = ' '.join(value.split())
        
        if len(normalized) < 3:
            return False, None, "Assunto muito curto"
        
        return True, normalized, ""
    
    def _validate_decision_type(self, value: str) -> Tuple[bool, Optional[str], str]:
        """Valida tipo de decisão"""
        if not value or value.lower() in ['null', 'none', 'n/a']:
            return True, None, ""
        
        normalized = ' '.join(value.split()).lower()
        
        # Tipos comuns de decisão
        valid_types = [
            'sentença', 'acórdão', 'despacho', 'decisão', 'liminar',
            'judgment', 'order', 'decree', 'ruling', 'decision'
        ]
        
        # Verifica se contém algum tipo válido
        contains_valid = any(vtype in normalized for vtype in valid_types)
        
        if not contains_valid:
            logger.warning(f"Tipo de decisão incomum: {value}")
        
        return True, value, ""
    
    def _validate_result(self, value: str) -> Tuple[bool, Optional[str], str]:
        """Valida resultado da decisão"""
        if not value or value.lower() in ['null', 'none', 'n/a']:
            return True, None, ""
        
        normalized = value.lower()
        
        # Verifica se contém palavra-chave válida
        contains_valid = any(valid_result in normalized for valid_result in self.valid_results)
        
        if not contains_valid:
            return False, None, f"Resultado inválido. Esperado um de: {', '.join(settings.VALID_RESULTS)}"
        
        return True, value, ""
    
    def _validate_summary(self, value: str) -> Tuple[bool, Optional[str], str]:
        """Valida resumo"""
        if not value or value.lower() in ['null', 'none', 'n/a']:
            return False, None, "Resumo é obrigatório"
        
        # Conta linhas
        lines = [line.strip() for line in value.split('\n') if line.strip()]
        num_lines = len(lines)
        
        if num_lines < settings.MIN_SUMMARY_LINES:
            return False, None, f"Resumo muito curto (mínimo {settings.MIN_SUMMARY_LINES} linha)"
        
        if num_lines > settings.MAX_SUMMARY_LINES:
            # Trunca para 5 linhas
            truncated = '\n'.join(lines[:settings.MAX_SUMMARY_LINES])
            logger.warning(f"Resumo truncado de {num_lines} para {settings.MAX_SUMMARY_LINES} linhas")
            return True, truncated, ""
        
        return True, value, ""
    
    def _validate_date(self, value: str) -> Tuple[bool, Optional[str], str]:
        """Valida e normaliza data"""
        if not value or value.lower() in ['null', 'none', 'n/a']:
            return True, None, ""
        
        # Tenta parsear diferentes formatos
        date_formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%d %B %Y',
            '%B %d, %Y',
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(value, fmt)
                # Normaliza para DD/MM/YYYY
                normalized = date_obj.strftime('%d/%m/%Y')
                return True, normalized, ""
            except ValueError:
                continue
        
        # Se não conseguiu parsear, tenta extrair com regex
        date_pattern = r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})'
        match = re.search(date_pattern, value)
        
        if match:
            day, month, year = match.groups()
            normalized = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
            return True, normalized, ""
        
        logger.warning(f"Data em formato não reconhecido: {value}")
        return True, value, ""
    
    def _validate_court(self, value: str) -> Tuple[bool, Optional[str], str]:
        """Valida nome do tribunal"""
        if not value or value.lower() in ['null', 'none', 'n/a']:
            return True, None, ""
        
        normalized = ' '.join(value.split())
        
        if len(normalized) < 3:
            return False, None, "Nome do tribunal muito curto"
        
        return True, normalized, ""
    
    def calculate_completeness(self, entities: Dict) -> float:
        """
        Calcula o percentual de completude das entidades
        
        Args:
            entities: Dicionário de entidades
            
        Returns:
            Percentual de 0 a 1
        """
        total_fields = len(settings.ENTITIES)
        filled_fields = sum(
            1 for key in settings.ENTITIES 
            if entities.get(key) and str(entities[key]).lower() not in ['null', 'none', 'n/a', '']
        )
        
        return filled_fields / total_fields if total_fields > 0 else 0.0
    
    def get_missing_fields(self, entities: Dict) -> List[str]:
        """
        Retorna lista de campos ausentes ou vazios
        
        Args:
            entities: Dicionário de entidades
            
        Returns:
            Lista de campos ausentes
        """
        missing = []
        
        for key in settings.ENTITIES:
            value = entities.get(key)
            if not value or str(value).lower() in ['null', 'none', 'n/a', '']:
                missing.append(key)
        
        return missing