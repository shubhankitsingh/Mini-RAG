"""
RAG Application Backend - FastAPI
Handles document ingestion, retrieval, reranking, and LLM answering
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import time
import os
import uuid
from dotenv import load_dotenv

from .rag_engine import RAGEngine
from .models import QueryRequest, QueryResponse, IngestRequest, IngestResponse

load_dotenv()

app = FastAPI(
    title="RAG Application API",
    description="Retrieval-Augmented Generation with citations",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy initialize RAG Engine
rag_engine = None

def get_rag_engine():
    global rag_engine
    if rag_engine is None:
        rag_engine = RAGEngine()
    return rag_engine


@app.get("/")
async def root():
    return {"status": "healthy", "message": "RAG API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest):
    """
    Ingest text content into the vector database.
    Chunks the text, generates embeddings, and stores with metadata.
    """
    start_time = time.time()
    
    try:
        # Generate unique source ID if not provided to prevent overwrites
        source = request.source or f"user_input_{uuid.uuid4().hex[:8]}"
        
        result = await get_rag_engine().ingest_text(
            text=request.text,
            source=source,
            title=request.title or "Untitled Document"
        )
        
        processing_time = time.time() - start_time
        
        return IngestResponse(
            success=True,
            message=f"Successfully ingested {result['chunks_count']} chunks",
            chunks_count=result['chunks_count'],
            processing_time_ms=round(processing_time * 1000, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    title: Optional[str] = None
):
    """
    Ingest a text file into the vector database.
    """
    start_time = time.time()
    
    try:
        content = await file.read()
        text = content.decode('utf-8')
        filename = file.filename or "uploaded_file"
        
        # Add unique ID to filename to prevent overwrites when uploading same file multiple times
        unique_source = f"{filename}_{uuid.uuid4().hex[:8]}"
        
        result = await get_rag_engine().ingest_text(
            text=text,
            source=unique_source,
            title=title or filename
        )
        
        processing_time = time.time() - start_time
        
        return IngestResponse(
            success=True,
            message=f"Successfully ingested {result['chunks_count']} chunks from {file.filename}",
            chunks_count=result['chunks_count'],
            processing_time_ms=round(processing_time * 1000, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system:
    1. Retrieve relevant chunks from vector DB
    2. Rerank results
    3. Generate answer with citations
    """
    start_time = time.time()
    
    try:
        result = await get_rag_engine().query(
            query=request.query,
            top_k=request.top_k or 10,
            rerank_top_k=request.rerank_top_k or 5
        )
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            answer=result['answer'],
            citations=result['citations'],
            sources=result['sources'],
            processing_time_ms=round(processing_time * 1000, 2),
            retrieval_time_ms=result['retrieval_time_ms'],
            rerank_time_ms=result['rerank_time_ms'],
            llm_time_ms=result['llm_time_ms'],
            tokens_used=result.get('tokens_used', {}),
            cost_estimate=result.get('cost_estimate', 0.0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/clear")
async def clear_index():
    """Clear all documents from the vector database."""
    try:
        await get_rag_engine().clear_index()
        return {"success": True, "message": "Index cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get statistics about the vector database."""
    try:
        stats = await get_rag_engine().get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
