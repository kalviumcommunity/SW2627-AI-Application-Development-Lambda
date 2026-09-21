CREATE TABLE IF NOT EXISTS kb_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES kb_documents(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    doc_type TEXT NOT NULL,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb, 
    embedding vector(384) NOT NULL, -- for now going with all-MiniLM-L6-v2 / 384
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_kb_embeddings_client_id ON kb_embeddings(client_id);
CREATE INDEX IF NOT EXISTS idx_kb_embeddings_doc_type ON kb_embeddings(doc_type);
CREATE INDEX IF NOT EXISTS idx_kb_embeddings_hnsw 
ON kb_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);