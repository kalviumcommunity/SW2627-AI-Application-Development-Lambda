CREATE OR REPLACE FUNCTION match_knowledge_chunks(
    query_embedding vector(384), -- using all-MiniLM-L6-v2 as default
    match_threshold FLOAT DEFAULT 0.5, -- tune later
    match_count INT DEFAULT 5, -- tune later
    filter_client_id UUID DEFAULT NULL,
    filter_doc_types TEXT[] DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    client_id UUID,
    doc_type TEXT,
    chunk_text TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ke.id,
        ke.document_id,
        ke.client_id,
        ke.doc_type,
        ke.chunk_text,
        ke.metadata,
        1 - (ke.embedding <=> query_embedding) AS similarity
    FROM kb_embeddings ke
    WHERE (filter_client_id IS NULL OR ke.client_id = filter_client_id)
      AND (filter_doc_types IS NULL OR ke.doc_type = ANY(filter_doc_types))
      AND (1 - (ke.embedding <=> query_embedding)) >= match_threshold
    ORDER BY ke.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
