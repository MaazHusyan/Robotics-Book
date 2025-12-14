-- RAG Chatbot Database Schema
-- Generated for Neon Postgres with Qdrant Cloud integration
-- Created: 2025-12-14

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Book Content Table
CREATE TABLE books_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_number INTEGER NOT NULL,
    chapter_title VARCHAR(255) NOT NULL,
    section_number INTEGER NOT NULL,
    section_title VARCHAR(255) NOT NULL,
    content_text TEXT NOT NULL,
    content_hash VARCHAR(64) UNIQUE NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Indexes for Book Content
CREATE INDEX idx_books_content_chapter_section ON books_content(chapter_number, section_number);
CREATE INDEX idx_books_content_hash ON books_content(content_hash);
CREATE INDEX idx_books_content_active ON books_content(is_active);

-- Conversations Table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL,
    user_query TEXT NOT NULL,
    chatbot_response TEXT NOT NULL,
    selected_text TEXT,
    selected_text_section_id UUID REFERENCES books_content(id),
    gemini_model_used VARCHAR(50),
    tokens_used INTEGER,
    response_time_ms INTEGER,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    is_helpful BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for Conversations
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_created ON conversations(created_at);
CREATE INDEX idx_conversations_section ON conversations(selected_text_section_id);

-- Embeddings Metadata Table
CREATE TABLE embeddings_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    books_content_id UUID NOT NULL REFERENCES books_content(id),
    qdrant_vector_id VARCHAR(255) NOT NULL,
    embedding_model VARCHAR(50) NOT NULL,
    chunk_index INTEGER DEFAULT 0,
    chunk_size INTEGER,
    vector_dimension INTEGER NOT NULL,
    metadata_json JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    last_synced_at TIMESTAMP,
    is_indexed BOOLEAN DEFAULT false,
    UNIQUE(books_content_id, chunk_index)
);

-- Indexes for Embeddings Metadata
CREATE INDEX idx_embeddings_content ON embeddings_metadata(books_content_id);
CREATE INDEX idx_embeddings_qdrant ON embeddings_metadata(qdrant_vector_id);

-- Sessions Table
CREATE TABLE sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_identifier VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity_at TIMESTAMP DEFAULT NOW(),
    browser_info JSONB,
    is_active BOOLEAN DEFAULT true,
    conversation_count INTEGER DEFAULT 0
);

-- Indexes for Sessions
CREATE INDEX idx_sessions_created ON sessions(created_at);
CREATE INDEX idx_sessions_user ON sessions(user_identifier);
CREATE INDEX idx_sessions_active ON sessions(is_active);

-- Foreign Key Constraints
ALTER TABLE conversations 
ADD CONSTRAINT fk_conversations_section 
FOREIGN KEY (selected_text_section_id) REFERENCES books_content(id) ON DELETE SET NULL;

ALTER TABLE embeddings_metadata 
ADD CONSTRAINT fk_embeddings_content 
FOREIGN KEY (books_content_id) REFERENCES books_content(id) ON DELETE CASCADE;

-- Triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_books_content_updated
    BEFORE UPDATE ON books_content
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_sessions_activity
    BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();