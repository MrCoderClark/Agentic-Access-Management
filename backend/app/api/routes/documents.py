"""API routes for document ingestion and RAG search."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.schemas.documents import (
    DocumentIngest,
    DocumentListResponse,
    DocumentResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.services.rag import rag_service

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/ingest", response_model=list[DocumentResponse])
async def ingest_document(body: DocumentIngest):
    """Ingest a document: chunk, embed, and store in vector DB."""
    try:
        results = await rag_service.ingest_document(
            content=body.content,
            doc_type=body.doc_type,
            metadata=body.metadata,
            source_id=body.source_id,
            chunk_size=body.chunk_size,
            chunk_overlap=body.chunk_overlap,
        )
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/ingest/file", response_model=list[DocumentResponse])
async def ingest_file(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    metadata: str = Form(default="{}"),
    source_id: str = Form(default=None),
):
    """Upload and ingest a text file."""
    import json

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Read file content
    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text")

    if not content.strip():
        raise HTTPException(status_code=400, detail="File is empty")

    # Parse metadata
    try:
        meta = json.loads(metadata)
    except json.JSONDecodeError:
        meta = {}

    meta["filename"] = file.filename
    meta["content_type"] = file.content_type

    sid = UUID(source_id) if source_id else None

    try:
        results = await rag_service.ingest_document(
            content=content,
            doc_type=doc_type,
            metadata=meta,
            source_id=sid,
        )
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_documents(body: SearchRequest):
    """Perform similarity search across documents."""
    try:
        if body.doc_types:
            results = await rag_service.search_multi(
                query=body.query,
                match_count=body.match_count,
                doc_types=body.doc_types,
                similarity_threshold=body.similarity_threshold,
            )
        else:
            results = await rag_service.search(
                query=body.query,
                match_count=body.match_count,
                doc_type=body.doc_type,
                similarity_threshold=body.similarity_threshold,
            )

        return SearchResponse(
            results=[SearchResult(**r) for r in results],
            query=body.query,
            count=len(results),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    doc_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    """List ingested documents (first chunk only)."""
    result = await rag_service.list_documents(
        doc_type=doc_type, limit=limit, offset=offset
    )
    return result


@router.delete("/by-source/{source_id}")
async def delete_by_source(source_id: UUID):
    """Delete all chunks for a source document."""
    count = await rag_service.delete_by_source(source_id)
    if count == 0:
        raise HTTPException(status_code=404, detail="No documents found for this source")
    return {"deleted_chunks": count}


@router.delete("/{document_id}")
async def delete_document(document_id: UUID):
    """Delete a single document chunk by its ID, plus all sibling chunks."""
    count = await rag_service.delete_by_id(document_id)
    if count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted_chunks": count}
