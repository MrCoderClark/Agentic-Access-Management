"""RAG service — document ingestion, retrieval, and context assembly."""

from uuid import UUID

from app.api.deps import get_supabase_client
from app.config import settings
from app.services.chunking import chunk_text, TextChunk
from app.services.embeddings import embedding_service


class RAGService:
    """Handles document ingestion and similarity-based retrieval."""

    def __init__(self):
        self.table = "documents"
        self.schema = "agentguard"

    def _client(self):
        return get_supabase_client()

    async def ingest_document(
        self,
        content: str,
        doc_type: str,
        metadata: dict | None = None,
        source_id: UUID | None = None,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
    ) -> list[dict]:
        """Chunk, embed, and store a document.

        Returns list of inserted document records.
        """
        chunks = chunk_text(content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        if not chunks:
            return []

        # Generate embeddings in batch
        texts = [c.content for c in chunks]
        embeddings = await embedding_service.embed_batch(texts)

        # Prepare rows for insertion
        rows = []
        for chunk, embedding in zip(chunks, embeddings):
            row = {
                "content": chunk.content,
                "doc_type": doc_type,
                "metadata": metadata or {},
                "source_id": str(source_id) if source_id else None,
                "embedding": embedding,
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count,
            }
            rows.append(row)

        # Insert into Supabase
        client = self._client()
        result = client.schema(self.schema).table(self.table).insert(rows).execute()
        return result.data

    async def search(
        self,
        query: str,
        match_count: int = 10,
        doc_type: str | None = None,
        similarity_threshold: float = 0.0,
    ) -> list[dict]:
        """Perform similarity search using the DB match_documents function."""
        query_embedding = await embedding_service.embed_text(query)

        client = self._client()
        result = client.schema(self.schema).rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_count": match_count,
                "filter_type": doc_type,
                "similarity_threshold": similarity_threshold,
            },
        ).execute()

        return result.data

    async def search_multi(
        self,
        query: str,
        match_count: int = 10,
        doc_types: list[str] | None = None,
        similarity_threshold: float = 0.0,
    ) -> list[dict]:
        """Search across multiple doc types."""
        query_embedding = await embedding_service.embed_text(query)

        client = self._client()
        result = client.schema(self.schema).rpc(
            "match_documents_multi",
            {
                "query_embedding": query_embedding,
                "match_count": match_count,
                "filter_types": doc_types,
                "similarity_threshold": similarity_threshold,
            },
        ).execute()

        return result.data

    async def delete_by_source(self, source_id: UUID) -> int:
        """Delete all chunks associated with a source document."""
        client = self._client()
        result = (
            client.schema(self.schema)
            .table(self.table)
            .delete()
            .eq("source_id", str(source_id))
            .execute()
        )
        return len(result.data)

    async def delete_by_id(self, document_id: UUID) -> int:
        """Delete a document and all its sibling chunks.

        Finds the document by ID, then deletes all chunks with matching
        metadata and doc_type (i.e. chunks from the same ingestion).
        """
        import json

        client = self._client()

        # First get the document to find its metadata for sibling matching
        doc = (
            client.schema(self.schema)
            .table(self.table)
            .select("id, metadata, doc_type, created_at")
            .eq("id", str(document_id))
            .execute()
        ).data

        if not doc:
            return 0

        doc = doc[0]
        metadata = doc["metadata"]

        # Use PostgREST containment operator for JSONB matching
        query = (
            client.schema(self.schema)
            .table(self.table)
            .delete()
            .eq("doc_type", doc["doc_type"])
            .filter("metadata", "cs", json.dumps(metadata))
        )
        result = query.execute()
        return len(result.data)

    async def list_documents(
        self,
        doc_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        """List stored documents (grouped by source_id, first chunk only)."""
        client = self._client()
        query = (
            client.schema(self.schema)
            .table(self.table)
            .select("id, content, doc_type, source_id, metadata, chunk_index, token_count, created_at")
            .eq("chunk_index", 0)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
        )
        if doc_type:
            query = query.eq("doc_type", doc_type)

        result = query.execute()
        return {"data": result.data, "count": len(result.data)}


rag_service = RAGService()
