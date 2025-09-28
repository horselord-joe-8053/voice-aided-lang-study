#!/usr/bin/env python3
"""
Unified FastAPI application that combines Text2Query and RAG capabilities.
Provides a single API endpoint that intelligently routes between approaches.
"""

from typing import Dict, Any, List, Optional
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from config.settings import load_system_config, get_profile
from config.logging_config import get_logger, log_system_info
from core.unified_engine import UnifiedQueryEngine
from reports.generic_report_builder import generate_report_from_question, ReportConfig

# Get logger
logger = get_logger(__name__)

# Pydantic models
class QuestionRequest(BaseModel):
    question: str = Field(..., description="The question to ask about the data")
    method: str = Field("auto", description="Query method: 'auto', 'text2query', 'rag', or 'both'")

class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict[str, Any]]
    confidence: str
    method_used: str
    execution_time: float
    timestamp: str
    profile: str
    report_url: Optional[str] = None
    report_meta: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str = Field(..., description="The search query")
    top_k: int = Field(10, ge=1, le=50, description="Number of results to return")

class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total_found: int

class StatsResponse(BaseModel):
    profile: str
    data: Dict[str, Any]
    engines: Dict[str, Any]
    text2query: Optional[Dict[str, Any]] = None
    rag: Optional[Dict[str, Any]] = None

class RebuildResponse(BaseModel):
    status: str
    message: str

class MethodResponse(BaseModel):
    available_methods: List[str]
    current_profile: str

# Global variables
config = None
unified_engine: UnifiedQueryEngine = None

def get_config():
    """Get the system configuration."""
    global config
    if config is None:
        config = load_system_config()
    return config

def get_unified_engine() -> UnifiedQueryEngine:
    """Get the unified engine instance."""
    global unified_engine
    if unified_engine is None:
        unified_engine = UnifiedQueryEngine()
    return unified_engine

# Create FastAPI app
app = FastAPI(
    title="Unified QueryRAG System",
    description="Combined Text2Query and RAG System - Profile-Aware",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    if os.environ.get("SKIP_STARTUP_INIT") == "1":
        logger.info("Skipping startup initialization due to SKIP_STARTUP_INIT=1")
        return
    
    # Log system information
    log_system_info()
    
    logger.info("Starting Unified QueryRAG System...")
    
    # Initialize configuration
    global config
    config = get_config()
    
    # Initialize unified engine
    try:
        global unified_engine
        unified_engine = get_unified_engine()
        logger.info("Unified engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize unified engine: {e}")
        raise
    
    logger.info("Unified QueryRAG System started successfully")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Unified QueryRAG System API",
        "version": "1.0.0",
        "status": "running",
        "description": "Combined Text2Query and RAG system with intelligent routing"
    }

@app.get("/health")
async def health_check(engine: UnifiedQueryEngine = Depends(get_unified_engine)):
    """Health check endpoint."""
    try:
        stats = engine.get_stats()
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "profile": stats.get("profile", "unknown"),
            "engines": stats.get("engines", {}),
            "data_records": stats.get("data", {}).get("total_records", 0)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, engine: UnifiedQueryEngine = Depends(get_unified_engine)):
    """
    Ask a question using the unified system.
    The system will try Text2Query first, then fallback to RAG if needed.
    """
    try:
        logger.info(f"Processing question: {request.question} (method: {request.method})")
        
        # Get answer from unified engine
        result = engine.answer_question(request.question, request.method)
        
        # Generate report if requested
        report_url = None
        report_meta = None
        
        # Check if question contains report-related keywords
        report_keywords = ["report", "pdf", "document", "summary", "export"]
        if any(keyword in request.question.lower() for keyword in report_keywords):
            try:
                profile = get_profile()
                report_config = profile.get_report_config()
                data_file = profile.get_data_file_path()
                
                report_path, meta = generate_report_from_question(
                    request.question,
                    data_file,
                    report_config
                )
                report_url = f"/reports/{Path(report_path).name}"
                report_meta = meta
                logger.info(f"Report generated: {report_path}")
            except Exception as e:
                logger.warning(f"Failed to generate report: {e}")
        
        return QuestionResponse(
            question=result["question"] if "question" in result else request.question,
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"],
            method_used=result["method_used"],
            execution_time=result["execution_time"],
            timestamp=result["timestamp"],
            profile=result["profile"],
            report_url=report_url,
            report_meta=report_meta
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {e}")

@app.post("/search", response_model=SearchResponse)
async def search_data(request: SearchRequest, engine: UnifiedQueryEngine = Depends(get_unified_engine)):
    """Search for relevant data chunks using RAG."""
    try:
        logger.info(f"Searching for: {request.query}")
        
        # Search for relevant chunks
        results = engine.search_data(request.query, request.top_k)
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_found=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error searching data: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching data: {e}")

@app.get("/stats", response_model=StatsResponse)
async def get_stats(engine: UnifiedQueryEngine = Depends(get_unified_engine)):
    """Get system statistics."""
    try:
        stats = engine.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {e}")

@app.get("/methods", response_model=MethodResponse)
async def get_available_methods(engine: UnifiedQueryEngine = Depends(get_unified_engine)):
    """Get available query methods."""
    try:
        methods = engine.get_available_methods()
        stats = engine.get_stats()
        return MethodResponse(
            available_methods=methods,
            current_profile=stats.get("profile", "unknown")
        )
    except Exception as e:
        logger.error(f"Error getting methods: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting methods: {e}")

@app.post("/rebuild", response_model=RebuildResponse)
async def rebuild_rag_index(engine: UnifiedQueryEngine = Depends(get_unified_engine)):
    """Rebuild the RAG vector store."""
    try:
        logger.info("Rebuilding RAG vector store...")
        
        success = engine.rebuild_rag_index()
        
        if success:
            return RebuildResponse(
                status="success",
                message="RAG vector store rebuilt successfully"
            )
        else:
            return RebuildResponse(
                status="error",
                message="Failed to rebuild RAG vector store"
            )
            
    except Exception as e:
        logger.error(f"Error rebuilding RAG vector store: {e}")
        raise HTTPException(status_code=500, detail=f"Error rebuilding RAG vector store: {e}")

@app.get("/reports/{filename}")
async def get_report(filename: str):
    """Download a generated report."""
    try:
        from reports.generic_report_builder import STORAGE_REPORTS_DIR
        
        file_path = STORAGE_REPORTS_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving report: {e}")
        raise HTTPException(status_code=500, detail=f"Error serving report: {e}")

@app.get("/profile")
async def get_profile_info():
    """Get current profile information."""
    try:
        profile = get_profile()
        stats = get_unified_engine().get_stats()
        
        return {
            "active_profile": profile.profile_name,
            "profile_name": profile.profile_name,
            "language": getattr(profile, 'language', 'en-US'),
            "locale": getattr(profile, 'locale', 'en_US'),
            "data_file_path": profile.get_data_file_path(),
            "data_schema": {
                "required_columns": profile.get_data_schema().required_columns,
                "sensitive_columns": profile.get_data_schema().sensitive_columns,
                "date_columns": profile.get_data_schema().date_columns,
                "text_columns": profile.get_data_schema().text_columns
            },
            "engines": stats.get("engines", {})
        }
    except Exception as e:
        logger.error(f"Error getting profile info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting profile info: {e}")

# Backward compatibility endpoints
@app.post("/ask-api")
async def ask_question_compat(request: QuestionRequest, engine: UnifiedQueryEngine = Depends(get_unified_engine)):
    """Backward compatibility endpoint for /ask-api."""
    return await ask_question(request, engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
