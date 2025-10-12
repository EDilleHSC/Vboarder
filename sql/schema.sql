CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    name TEXT,
    agent_role TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT,
    embedding vector(1536),
    chunk_index INT,
    metadata JSONB,
    token_count INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION match_chunks(query_embedding vector(1536), match_count int)
RETURNS TABLE(id int, content text, similarity float)
AS }
    SELECT id, content, 1 - (embedding <=> query_embedding) AS similarity
    FROM chunks
    ORDER BY embedding <-> query_embedding
    LIMIT match_count;
} LANGUAGE sql STABLE;
