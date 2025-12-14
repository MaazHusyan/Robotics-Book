# Feature Specification: RAG Chatbot Database

**Feature Branch**: `001-rag-chatbot`  
**Created**: 2025-12-14  
**Status**: Draft  
**Input**: User description: "rag-chatbot database specification"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Content Ingestion (Priority: P1)

As a system administrator, I want to automatically ingest book content from Docusaurus MDX files so that the chatbot has comprehensive knowledge of robotics book material.

**Why this priority**: Essential for chatbot functionality - without ingested content, no answers can be provided

**Independent Test**: Can be fully tested by running ingestion script on existing MDX files and verifying content appears in database

**Acceptance Scenarios**:

1. **Given** existing MDX files in docs/ directory, **When** ingestion script runs, **Then** all chapters and sections are stored in books_content table
2. **Given** duplicate content files, **When** ingestion runs, **Then** duplicates are prevented by content_hash constraint

---

### User Story 2 - Semantic Question Answering (Priority: P1)

As a reader, I want to ask questions about robotics topics and receive accurate answers with source citations so that I can learn from the book content.

**Why this priority**: Core functionality - this is the primary value proposition of the RAG chatbot

**Independent Test**: Can be fully tested by asking sample robotics questions and verifying responses include accurate citations

**Acceptance Scenarios**:

1. **Given** ingested book content, **When** user asks "What is Zero Moment Point?", **Then** chatbot provides accurate definition with chapter/section citation
2. **Given** complex multi-part question, **When** user submits query, **Then** response synthesizes information from multiple relevant sections

---

### User Story 3 - Text Selection Context (Priority: P2)

As a reader, I want to select specific text passages and ask questions about them so that I can get contextual answers focused on my selected content.

**Why this priority**: Enhances user experience by allowing focused inquiry on specific topics

**Independent Test**: Can be fully tested by selecting text and verifying chatbot responses reference the selected passage

**Acceptance Scenarios**:

1. **Given** selected text from a chapter, **When** user asks follow-up question, **Then** response prioritizes selected content context
2. **Given** multiple text selections, **When** user combines them in query, **Then** chatbot synthesizes across all selected passages

---

### User Story 4 - Conversation History (Priority: P2)

As a reader, I want to see my conversation history so that I can review previous questions and answers.

**Why this priority**: Improves user experience and enables learning continuity

**Independent Test**: Can be fully tested by having multiple conversations and verifying history is retrievable

**Acceptance Scenarios**:

1. **Given** previous conversations in same session, **When** user requests history, **Then** all Q&A pairs are displayed chronologically
2. **Given** session timeout, **When** user returns later, **Then** conversation history is restored if session is still active

---

## Requirements *(mandatory)*

### RAG Chatbot Functional Requirements

- **RC-001**: Chatbot MUST answer questions about Physical and Humanoid Robotics book content
- **RC-002**: Chatbot MUST support user text selection for context enhancement
- **RC-003**: Chatbot MUST provide source citations for all responses
- **RC-004**: Chatbot MUST integrate seamlessly with Docusaurus site

### Technical Integration Requirements

- **TI-001**: Frontend MUST use React 19.0.0 components embedded in Docusaurus
- **TI-002**: Backend MUST use FastAPI with REST API endpoints
- **TI-003**: Vector storage MUST use Qdrant Cloud Free Tier
- **TI-004**: Metadata storage MUST use Neon serverless Postgres
- **TI-005**: LLM integration MUST use Google Gemini (custom integration, not OpenAI)

### Database Schema Requirements

- **DB-001**: Neon Postgres MUST store book content with chapter/section structure
- **DB-002**: Neon Postgres MUST track conversation history with session management
- **DB-003**: Neon Postgres MUST maintain embedding metadata with Qdrant references
- **DB-004**: Qdrant Cloud MUST store vectors with cosine similarity search
- **DB-005**: Schema MUST support content deduplication and soft deletes

### Performance Requirements

- **PR-001**: Book content retrieval MUST be under 100ms
- **PR-002**: Vector search (Qdrant) MUST be under 200ms
- **PR-003**: Total RAG response time MUST be under 3-5 seconds
- **PR-004**: System MUST support 10-50 concurrent users on free tiers

### Quality Assurance Requirements

- **QR-001**: RAG answer accuracy MUST be tested with sample robotics questions
- **QR-002**: Response time benchmarks MUST be validated under load
- **QR-003**: API error handling MUST be tested for resilience
- **QR-004**: Content accuracy MUST be validated against book source material

### Key Entities *(include if feature involves data)*

- **Book Content**: Represents chapters and sections from robotics book with attributes: id, chapter_number, section_number, title, content_text, source_file
- **Conversation**: Represents user-chatbot interactions with attributes: id, session_id, user_query, chatbot_response, selected_text, response_time
- **Embedding Metadata**: Represents vector storage references with attributes: id, books_content_id, qdrant_vector_id, embedding_model, chunk_index
- **Session**: Represents user conversation sessions with attributes: id, user_identifier, created_at, conversation_count

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Chatbot successfully embedded in Docusaurus site with functional UI
- **SC-002**: Chatbot can answer book-related questions with 95% accuracy
- **SC-003**: Text selection feature works with 99% success rate
- **SC-004**: Response time consistently under 3 seconds for typical queries
- **SC-005**: All 13 existing book chapters successfully ingested and indexed
- **SC-006**: System maintains conversation history with session continuity

## Database Design Specification

### Neon Postgres Schema

#### Database: robotics_book

**Table: books_content**
```sql
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

CREATE INDEX idx_books_content_chapter_section ON books_content(chapter_number, section_number);
CREATE INDEX idx_books_content_hash ON books_content(content_hash);
CREATE INDEX idx_books_content_active ON books_content(is_active);
```

**Table: conversations**
```sql
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

CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_created ON conversations(created_at);
CREATE INDEX idx_conversations_section ON conversations(selected_text_section_id);
```

**Table: embeddings_metadata**
```sql
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

CREATE INDEX idx_embeddings_content ON embeddings_metadata(books_content_id);
CREATE INDEX idx_embeddings_qdrant ON embeddings_metadata(qdrant_vector_id);
```

**Table: sessions**
```sql
CREATE TABLE sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_identifier VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity_at TIMESTAMP DEFAULT NOW(),
    browser_info JSONB,
    is_active BOOLEAN DEFAULT true,
    conversation_count INTEGER DEFAULT 0
);

CREATE INDEX idx_sessions_created ON sessions(created_at);
CREATE INDEX idx_sessions_user ON sessions(user_identifier);
CREATE INDEX idx_sessions_active ON sessions(is_active);
```

### Qdrant Cloud Collection

**Collection: robotics_book_embeddings**

```json
{
    "name": "robotics_book_embeddings",
    "vector_size": 768,
    "distance": "Cosine",
    "payload_schema": {
        "books_content_id": "uuid",
        "chapter_number": "integer",
        "section_number": "integer", 
        "section_title": "text",
        "chapter_title": "text",
        "content_chunk": "text",
        "source_file": "text",
        "word_count": "integer",
        "created_at": "datetime"
    },
    "hnsw_config": {
        "m": 16,
        "ef_construct": 200
    }
}
```

### Data Flow Architecture

**Ingestion Pipeline:**
1. Parse MDX files → Extract chapters/sections → Store in books_content
2. Generate embeddings → Store vectors in Qdrant → Store metadata in embeddings_metadata
3. Update is_indexed flags when sync complete

**Query Pipeline:**
1. User question → Generate embedding → Search Qdrant (top-k results)
2. Retrieve books_content from Neon → Build context → Query Gemini
3. Store conversation → Return response with citations

**Session Management:**
1. Create/retrieve session → Track conversation count → Update last_activity_at
2. Store all Q&A pairs → Enable history retrieval

## Assumptions

- Google Gemini embedding model will be used (not OpenAI)
- Vector dimension will be 768 (typical for Gemini embeddings)
- Content chunking at 512 tokens for large sections
- Session timeout after 24 hours of inactivity
- No user authentication required (anonymous sessions)

## Dependencies

- Neon serverless Postgres instance (connection via .env)
- Qdrant Cloud Free Tier account
- Google Gemini API access
- Existing Docusaurus 3.9.2 site structure