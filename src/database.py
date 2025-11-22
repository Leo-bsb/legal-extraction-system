"""
Módulo para persistência de dados em SQLite
"""
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import sqlite3
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Gerenciador do banco de dados SQLite"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Inicializa conexão com o banco
        
        Args:
            db_path: Caminho para o arquivo do banco
        """
        self.db_path = db_path or settings.DB_PATH
        self.conn = None
        self.cursor = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Cria tabelas se não existirem"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Tabela principal de casos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL,
                autor TEXT,
                reu TEXT,
                assunto_principal TEXT,
                tipo_decisao TEXT,
                resultado TEXT,
                resumo_5_linhas TEXT,
                data_decisao TEXT,
                tribunal TEXT,
                language TEXT,
                year TEXT,
                completeness_score REAL,
                validation_errors TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de métricas de processamento
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                extraction_time REAL,
                num_retries INTEGER,
                success BOOLEAN,
                error_message TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_filename ON cases(filename)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_year ON cases(year)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_resultado ON cases(resultado)
        ''')
        
        self.conn.commit()
        logger.info(f"Banco de dados inicializado: {self.db_path}")
    
    def insert_case(self, filename: str, entities: Dict, 
                   language: str = 'en', year: Optional[str] = None,
                   completeness_score: float = 0.0,
                   validation_errors: Optional[List[str]] = None) -> bool:
        """
        Insere um caso no banco
        
        Args:
            filename: Nome do arquivo
            entities: Dicionário de entidades
            language: Idioma do documento
            year: Ano do caso
            completeness_score: Score de completude
            validation_errors: Erros de validação
            
        Returns:
            True se sucesso
        """
        try:
            errors_json = json.dumps(validation_errors) if validation_errors else None
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO cases 
                (filename, autor, reu, assunto_principal, tipo_decisao, 
                 resultado, resumo_5_linhas, data_decisao, tribunal,
                 language, year, completeness_score, validation_errors, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                filename,
                entities.get('autor'),
                entities.get('reu'),
                entities.get('assunto_principal'),
                entities.get('tipo_decisao'),
                entities.get('resultado'),
                entities.get('resumo_5_linhas'),
                entities.get('data_decisao'),
                entities.get('tribunal'),
                language,
                year,
                completeness_score,
                errors_json
            ))
            
            self.conn.commit()
            logger.info(f"Caso inserido: {filename}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Erro ao inserir caso {filename}: {e}")
            return False
    
    def insert_metric(self, filename: str, extraction_time: float,
                     num_retries: int, success: bool,
                     error_message: Optional[str] = None) -> bool:
        """
        Insere métrica de processamento
        
        Args:
            filename: Nome do arquivo
            extraction_time: Tempo de extração (segundos)
            num_retries: Número de tentativas
            success: Se foi bem-sucedido
            error_message: Mensagem de erro
            
        Returns:
            True se sucesso
        """
        try:
            self.cursor.execute('''
                INSERT INTO processing_metrics
                (filename, extraction_time, num_retries, success, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (filename, extraction_time, num_retries, success, error_message))
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Erro ao inserir métrica: {e}")
            return False
    
    def get_case(self, filename: str) -> Optional[Dict]:
        """
        Busca um caso pelo filename
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Dicionário com dados do caso ou None
        """
        try:
            self.cursor.execute('SELECT * FROM cases WHERE filename = ?', (filename,))
            row = self.cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Erro ao buscar caso: {e}")
            return None
    
    def get_all_cases(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Retorna todos os casos
        
        Args:
            limit: Limite de resultados
            
        Returns:
            Lista de dicionários
        """
        try:
            query = 'SELECT * FROM cases ORDER BY created_at DESC'
            if limit:
                query += f' LIMIT {limit}'
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except sqlite3.Error as e:
            logger.error(f"Erro ao buscar casos: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas do banco
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            stats = {}
            
            # Total de casos
            self.cursor.execute('SELECT COUNT(*) as total FROM cases')
            stats['total_cases'] = self.cursor.fetchone()['total']
            
            # Média de completude
            self.cursor.execute('SELECT AVG(completeness_score) as avg_completeness FROM cases')
            stats['avg_completeness'] = self.cursor.fetchone()['avg_completeness'] or 0.0
            
            # Casos por ano
            self.cursor.execute('''
                SELECT year, COUNT(*) as count 
                FROM cases 
                WHERE year IS NOT NULL 
                GROUP BY year 
                ORDER BY year
            ''')
            stats['cases_by_year'] = {row['year']: row['count'] for row in self.cursor.fetchall()}
            
            # Distribuição de resultados
            self.cursor.execute('''
                SELECT resultado, COUNT(*) as count 
                FROM cases 
                WHERE resultado IS NOT NULL 
                GROUP BY resultado 
                ORDER BY count DESC
            ''')
            stats['result_distribution'] = {row['resultado']: row['count'] for row in self.cursor.fetchall()}
            
            # Taxa de sucesso no processamento
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM processing_metrics
            ''')
            metrics = self.cursor.fetchone()
            if metrics['total'] > 0:
                stats['processing_success_rate'] = metrics['successful'] / metrics['total']
            else:
                stats['processing_success_rate'] = 0.0
            
            return stats
            
        except sqlite3.Error as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}
    
    def export_to_csv(self, output_path: Path) -> bool:
        """
        Exporta casos para CSV
        
        Args:
            output_path: Caminho para o arquivo CSV
            
        Returns:
            True se sucesso
        """
        try:
            import csv
            
            cases = self.get_all_cases()
            
            if not cases:
                logger.warning("Nenhum caso para exportar")
                return False
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=cases[0].keys())
                writer.writeheader()
                writer.writerows(cases)
            
            logger.info(f"Dados exportados para: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar CSV: {e}")
            return False
    
    def close(self):
        """Fecha conexão com o banco"""
        if self.conn:
            self.conn.close()
            logger.info("Conexão com banco fechada")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()