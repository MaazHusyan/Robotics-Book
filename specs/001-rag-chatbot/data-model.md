# Data Model: RAG Chatbot

**Date**: 2025-12-14  
**Feature**: RAG Chatbot Implementation  
**Status**: COMPLETED

## Entity Definitions

### BookContent

Represents individual chapters and sections from the Physical and Humanoid Robotics book.

**Attributes**:
- **id**: UUID (Primary Key) - Unique identifier for each content record
- **chapter_number**: Integer - Sequential chapter number (1, 2, 3...)
- **chapter_title**: String(255) - Human-readable chapter title
- **section_number**: Integer - Sequential section number within chapter
- **section_title**: String(255) - Human-readable section title
- **content_text**: Text - Full MDX content of the section
- **content_hash**: String(64) - MD5/SHA256 hash for deduplication
- **source_file**: String(255) - Original MDX file path
- **word_count**: Integer - Total word count for statistics
- **created_at**: Timestamp - Record creation timestamp
- **updated_at**: Timestamp - Last modification timestamp
- **is_active**: Boolean - Soft delete flag for content management

**Validation Rules**:
- content_hash must be unique across all records
- chapter_number and section_number combination must be unique within active content
- word_count must be >= 0
- source_file must reference existing MDX file

### Conversation

Represents individual chat interactions between users and the RAG chatbot.

**Attributes**:
- **id**: UUID (Primary Key) - Unique conversation identifier
- **session_id**: String(255) - Links multiple conversations in same session
- **user_query**: Text - User's original question or prompt
- **chatbot_response**: Text - Chatbot's generated response
- **selected_text**: Text (Optional) - User-selected text for context enhancement
- **selected_text_section_id**: UUID (Foreign Key) - Reference to BookContent if text selected
- **gemini_model_used**: String(50) - Gemini model version for tracking
- **tokens_used**: Integer - API token consumption for cost tracking
- **response_time_ms**: Integer - Performance monitoring metric
- **confidence_score**: Float(0-1) - RAG relevance confidence
- **is_helpful**: Boolean (Optional) - User feedback on response quality
- **created_at**: Timestamp - Conversation timestamp

**Validation Rules**:
- session_id must reference valid session in sessions table
- response_time_ms must be >= 0
- confidence_score must be between 0 and 1 inclusive
- tokens_used must be >= 0
- selected_text_section_id must reference valid BookContent if provided

### EmbeddingMetadata

Tracks vector embeddings and their relationship to book content.

**Attributes**:
- **id**: UUID (Primary Key) - Unique embedding metadata identifier
- **books_content_id**: UUID (Foreign Key) - Reference to BookContent
- **qdrant_vector_id**: String(255) - Vector identifier in Qdrant collection
- **embedding_model**: String(50) - Model used for embedding generation
- **chunk_index**: Integer - Chunk number for large content sections
- **chunk_size**: Integer - Token count per chunk
- **vector_dimension**: Integer - Embedding vector dimensions (768 for Gemini)
- **metadata_json**: JSONB - Additional metadata in flexible format
- **created_at**: Timestamp - Embedding generation timestamp
- **last_synced_at**: Timestamp (Optional) - Last Qdrant synchronization
- **is_indexed**: Boolean - Confirmation of successful vector storage

**Validation Rules**:
- books_content_id must reference valid BookContent record
- qdrant_vector_id must be unique across embeddings
- chunk_index must be >= 0 for chunked content
- vector_dimension must match embedding model specifications
- Unique constraint on (books_content_id, chunk_index) combination

### Session

Manages user conversation sessions for continuity and analytics.

**Attributes**:
- **id**: String(255) (Primary Key) - Unique session identifier
- **user_identifier**: String(255) - Browser fingerprint or user ID
- **created_at**: Timestamp - Session creation time
- **last_activity_at**: Timestamp - Last interaction time
- **browser_info**: JSONB - User agent and device information
- **is_active**: Boolean - Session status for cleanup
- **conversation_count**: Integer - Total conversations in session

**Validation Rules**:
- id must be unique across all active sessions
- conversation_count must be >= 0
- last_activity_at must be >= created_at
- Sessions inactive for >24 hours without activity

## Entity Relationships

```
BookContent (1) ----< (1:N) ---- EmbeddingMetadata
    |
    |                                    |
    |                                    |
    |                                    |
    
Session (1) ----< (1:N) ---- Conversation
    |
    |
    |
    
BookContent (1) ----< (Optional) ---- Conversation.selected_text_section_id
```

## State Transitions

### Session Lifecycle
1. **Created** → **Active** (initial state)
2. **Active** → **Inactive** (after 24 hours of inactivity)
3. **Inactive** → **Removed** (cleanup process)

### Content Ingestion Flow
1. **Parsed** → **Pending Embedding** (MDX content extracted)
2. **Pending Embedding** → **Embedding Generated** (vectors created)
3. **Embedding Generated** → **Indexed** (stored in Qdrant)
4. **Indexed** → **Active** (available for RAG queries)

### Conversation Flow
1. **Session Created** → **User Query** → **RAG Processing** → **Response Generated** → **Conversation Stored**

## Data Integrity Constraints

### Referential Integrity
- All EmbeddingMetadata must reference valid BookContent
- All Conversations must reference valid Session (if session_id provided)
- Cascading deletes: Session deletion removes associated conversations

### Uniqueness Constraints
- BookContent.content_hash must be unique
- EmbeddingMetadata.qdrant_vector_id must be unique
- Session.id must be unique

### Performance Considerations
- Index on BookContent.content_hash for duplicate detection
- Composite index on EmbeddingMetadata(books_content_id, chunk_index)
- Index on Conversation.session_id for history retrieval
- Index on Session.last_activity_at for cleanup operations