-- =============================================================================
-- 002_pgvector_setup.sql — RAG vector store for AgentGuard
-- =============================================================================
-- Schema: agentguard
-- Enables pgvector extension, creates documents table, HNSW index,
-- and match_documents similarity search function.
-- =============================================================================

-- Enable pgvector extension (installed in public, available to all schemas)
CREATE EXTENSION IF NOT EXISTS vector;

-- Set search path
SET search_path TO agentguard, public;

-- Vector store for RAG documents
-- Dimension: 1536 for OpenAI text-embedding-3-small (default)
-- Change to 384 if using local all-MiniLM-L6-v2
CREATE TABLE agentguard.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    doc_type TEXT NOT NULL,          -- 'policy', 'runbook', 'decision', 'system_doc', 'compliance'
    source_id UUID,                  -- FK to the source record (policy, ticket, etc.)
    embedding VECTOR(1536),          -- adjust dimension to match your embedding model
    org_id UUID,                     -- tenant isolation for multi-org (future)
    chunk_index INT DEFAULT 0,       -- position within the source document
    token_count INT,                 -- token count of this chunk
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast approximate nearest neighbor search
CREATE INDEX idx_documents_embedding ON agentguard.documents USING hnsw (embedding vector_cosine_ops);

-- Filtering indexes
CREATE INDEX idx_documents_type ON agentguard.documents(doc_type);
CREATE INDEX idx_documents_source ON agentguard.documents(source_id);
CREATE INDEX idx_documents_org ON agentguard.documents(org_id) WHERE org_id IS NOT NULL;

-- Enable RLS
ALTER TABLE agentguard.documents ENABLE ROW LEVEL SECURITY;

-- Apply updated_at trigger
CREATE TRIGGER set_updated_at_documents
    BEFORE UPDATE ON agentguard.documents
    FOR EACH ROW EXECUTE FUNCTION agentguard.update_updated_at_column();

-- =============================================================================
-- Similarity search function
-- Returns top-k documents ordered by cosine similarity
-- Supports optional filtering by doc_type
-- =============================================================================
CREATE OR REPLACE FUNCTION agentguard.match_documents(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 10,
    filter_type TEXT DEFAULT NULL,
    similarity_threshold FLOAT DEFAULT 0.0
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    doc_type TEXT,
    source_id UUID,
    chunk_index INT,
    similarity FLOAT
)
AS $$
    SELECT
        d.id,
        d.content,
        d.metadata,
        d.doc_type,
        d.source_id,
        d.chunk_index,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM agentguard.documents d
    WHERE
        (filter_type IS NULL OR d.doc_type = filter_type)
        AND (1 - (d.embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
$$ LANGUAGE sql STABLE;

-- =============================================================================
-- Multi-type search function
-- Retrieves from multiple doc types in one call (for RAG context assembly)
-- =============================================================================
CREATE OR REPLACE FUNCTION agentguard.match_documents_multi(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 10,
    filter_types TEXT[] DEFAULT NULL,
    similarity_threshold FLOAT DEFAULT 0.0
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    doc_type TEXT,
    source_id UUID,
    chunk_index INT,
    similarity FLOAT
)
AS $$
    SELECT
        d.id,
        d.content,
        d.metadata,
        d.doc_type,
        d.source_id,
        d.chunk_index,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM agentguard.documents d
    WHERE
        (filter_types IS NULL OR d.doc_type = ANY(filter_types))
        AND (1 - (d.embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
$$ LANGUAGE sql STABLE;
