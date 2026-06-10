"""Schemas for document ingestion and RAG search."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentIngest(BaseModel):
    content: str = Field(..., min_length=1, description="Document text content")
    doc_type: str = Field(..., description="Type: policy, runbook, decision, system_doc, compliance")
    metadata: dict | None = Field(default=None, description="Arbitrary metadata")
    source_id: UUID | None = Field(default=None, description="FK to source record")
    chunk_size: int = Field(default=512, ge=64, le=2048)
    chunk_overlap: int = Field(default=64, ge=0, le=256)


class DocumentResponse(BaseModel):
    id: UUID
    content: str
    doc_type: str
    source_id: UUID | None = None
    metadata: dict = {}
    chunk_index: int = 0
    token_count: int | None = None
    created_at: datetime


class DocumentListResponse(BaseModel):
    data: list[DocumentResponse]
    count: int


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")
    match_count: int = Field(default=10, ge=1, le=50)
    doc_type: str | None = Field(default=None, description="Filter by document type")
    doc_types: list[str] | None = Field(default=None, description="Filter by multiple types")
    similarity_threshold: float = Field(default=0.0, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    id: UUID
    content: str
    metadata: dict = {}
    doc_type: str
    source_id: UUID | None = None
    chunk_index: int
    similarity: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str
    count: int
