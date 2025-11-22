"""
FastAPI Backend para o Sistema de Extração Jurídica
"""
import time
import logging
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import sys

# Adiciona o diretório src ao path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from pdf_processor import PDFProcessor
from text_cleaner import TextCleaner
from llm_extractor import LLMExtractor
from validator import EntityValidator
from database import Database
from metrics import MetricsCalculator
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa FastAPI
app = FastAPI(
    title="Legal Extraction API",
    description="API para extração de entidades jurídicas de PDFs usando LLM",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Componentes globais
pdf_processor = PDFProcessor()
text_cleaner = TextCleaner()
validator = EntityValidator()
db = Database()
metrics_calc = MetricsCalculator()

# Modelos Pydantic
class ExtractionResponse(BaseModel):
    filename: str
    entities: dict
    completeness: float
    validation_errors: List[str]
    processing_time: float
    language: str


class StatisticsResponse(BaseModel):
    total_cases: int
    avg_completeness: float
    success_rate: float
    cases_by_year: dict
    result_distribution: dict


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Legal Extraction API",
        "version": "1.0.0",
        "endpoints": {
            "extract": "/api/extract",
            "batch": "/api/batch",
            "cases": "/api/cases",
            "stats": "/api/statistics",
            "export": "/api/export"
        }
    }


@app.post("/api/extract", response_model=ExtractionResponse)
async def extract_from_pdf(
    file: UploadFile = File(...),
    language: Optional[str] = None
):
    """
    Extrai entidades de um único PDF
    
    Args:
        file: Arquivo PDF
        language: Idioma ('pt' ou 'en', auto-detectado se não fornecido)
    """
    start_time = time.time()
    
    try:
        # Salva arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)
        
        # Extrai texto
        text = pdf_processor.extract_text(tmp_path)
        
        if not text:
            raise HTTPException(status_code=400, detail="Não foi possível extrair texto do PDF")
        
        # Limpa texto
        clean_text = text_cleaner.clean(text)
        
        # Detecta idioma se não fornecido
        if not language:
            language = pdf_processor.detect_language(clean_text)
        
        # Trunca se necessário
        truncated_text = text_cleaner.truncate_for_llm(clean_text)
        
        # Extrai entidades
        try:
            extractor = LLMExtractor()
            entities = extractor.extract_entities(truncated_text, language)
        except Exception as e:
            logger.error(f"Erro ao inicializar LLM: {e}")
            raise HTTPException(status_code=500, detail=f"Erro na LLM: {str(e)}")
        
        if not entities:
            raise HTTPException(status_code=500, detail="Falha na extração de entidades")
        
        # Valida entidades
        is_valid, validated_entities, errors = validator.validate(entities)
        completeness = validator.calculate_completeness(validated_entities)
        
        # Salva no banco
        metadata = pdf_processor.get_metadata(tmp_path)
        db.insert_case(
            filename=file.filename,
            entities=validated_entities,
            language=language,
            year=metadata.year,
            completeness_score=completeness,
            validation_errors=errors
        )
        
        # Métricas
        processing_time = time.time() - start_time
        db.insert_metric(
            filename=file.filename,
            extraction_time=processing_time,
            num_retries=1,
            success=True
        )
        
        # Remove arquivo temporário
        tmp_path.unlink()
        
        return ExtractionResponse(
            filename=file.filename,
            entities=validated_entities,
            completeness=completeness,
            validation_errors=errors,
            processing_time=processing_time,
            language=language
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch")
async def extract_batch(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Processa múltiplos PDFs em batch
    
    Args:
        files: Lista de arquivos PDF
    """
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Máximo de 50 arquivos por batch")
    
    results = []
    
    for file in files:
        try:
            result = await extract_from_pdf(file)
            results.append({
                "filename": file.filename,
                "status": "success",
                "completeness": result.completeness
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    success_count = sum(1 for r in results if r["status"] == "success")
    
    return {
        "total": len(files),
        "successful": success_count,
        "failed": len(files) - success_count,
        "results": results
    }


@app.get("/api/cases")
async def get_cases(limit: Optional[int] = 100):
    """
    Retorna lista de casos processados
    
    Args:
        limit: Limite de resultados
    """
    cases = db.get_all_cases(limit=limit)
    return {"total": len(cases), "cases": cases}


@app.get("/api/cases/{filename}")
async def get_case(filename: str):
    """
    Retorna detalhes de um caso específico
    
    Args:
        filename: Nome do arquivo
    """
    case = db.get_case(filename)
    
    if not case:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    
    return case


@app.get("/api/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """Retorna estatísticas do sistema"""
    stats = db.get_statistics()
    
    return StatisticsResponse(
        total_cases=stats.get('total_cases', 0),
        avg_completeness=stats.get('avg_completeness', 0.0),
        success_rate=stats.get('processing_success_rate', 0.0),
        cases_by_year=stats.get('cases_by_year', {}),
        result_distribution=stats.get('result_distribution', {})
    )


@app.get("/api/export/csv")
async def export_csv():
    """Exporta todos os casos para CSV"""
    try:
        output_path = settings.RESULTS / f"export_{int(time.time())}.csv"
        success = db.export_to_csv(output_path)
        
        if success:
            return FileResponse(
                path=output_path,
                filename=output_path.name,
                media_type="text/csv"
            )
        else:
            raise HTTPException(status_code=500, detail="Erro ao exportar CSV")
            
    except Exception as e:
        logger.error(f"Erro ao exportar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Testa conexão com o banco
        stats = db.get_statistics()
        
        # Testa se a LLM está configurada
        llm_configured = bool(settings.GEMINI_API_KEY)
        
        return {
            "status": "healthy",
            "database": "connected",
            "llm_configured": llm_configured,
            "total_cases": stats.get('total_cases', 0)
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup ao desligar"""
    db.close()
    logger.info("API encerrada")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )