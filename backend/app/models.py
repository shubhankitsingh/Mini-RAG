"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class IngestRequest(BaseModel):
    """Request model for text ingestion"""
    text: str
    source: Optional[str] = "user_input"
    title: Optional[str] = "Untitled Document"


class IngestResponse(BaseModel):
    """Response model for ingestion"""
    success: bool
    message: str
    chunks_count: int
    processing_time_ms: float


class Citation(BaseModel):
    """Citation model for source references"""
    id: int
    text: str
    source: str
    title: str
    section: Optional[str] = None
    position: int
    relevance_score: float


class QueryRequest(BaseModel):
    """Request model for querying"""
    query: str
    top_k: Optional[int] = 10
    rerank_top_k: Optional[int] = 5


class QueryResponse(BaseModel):
    """Response model for query results"""
    answer: str
    citations: List[Citation]
    sources: List[Dict[str, Any]]
    processing_time_ms: float
    retrieval_time_ms: float
    rerank_time_ms: float
    llm_time_ms: float
    tokens_used: Dict[str, int]
    cost_estimate: float


class ChunkMetadata(BaseModel):
    """Metadata stored with each chunk in vector DB"""
    source: str
    title: str
    section: Optional[str] = None
    position: int  # Position of chunk in document
    chunk_index: int  # Index of chunk
    total_chunks: int
    char_start: int
    char_end: int
    text: str  # Store text for retrieval
