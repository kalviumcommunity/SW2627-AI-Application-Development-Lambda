# Ingestion Pipeline Step
1. Fetch Raw Files
    - Google Drive PDFs (via read_cods.py)
    - Supabase JSON Runbooks (via runbook_references table + Storage)
  
2. Document Hashing & Differential Check
    - Compute SHA-256 of extracted content
    - Compare with `knowledge_documents.content_hash`
    - Skip if unchanged! If changed/new, delete old chunks from `knowledge_embeddings`.
  
3. Cleaning & Chunking
    - Clean text using `cleaner.py`
    - Chunk with token overlap using `chunker.py` / `token_chunker.py`
    - Enrich each chunk with metadata (`client_id`, `source`, `doc_type`, `section`)

4. Embedding Generation
    - Batch embed text chunks using `embed_store.py` (Ollama/nomic-embed-text or OpenAI)
  
5. Supabase Database Upsert
    - Record update in `knowledge_documents`
    - Batch insert vector rows into `knowledge_embeddings`
