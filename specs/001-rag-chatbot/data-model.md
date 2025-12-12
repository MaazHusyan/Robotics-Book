# Data Model: Live Gemini RAG Tutor

**Date**: 2025-12-11  
**Purpose**: Entity definitions and relationships for RAG chatbot system

## Core Entities

### ContentChunk
Represents a segmented portion of book content optimized for retrieval.

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ChunkType(str, Enum):
    PARAGRAPH = "paragraph"
    SECTION = "section"
    CODE = "code"
    LIST = "list"

class ContentChunk(BaseModel):
    id: str  # UUID or hash
    content: str  # Text content (500-1000 chars)
    source_file: str  # Relative path to MDX file
    chapter: str  # Chapter directory name
    section: str  # Section name without extension
    chunk_index: int  # Order within file
    chunk_type: ChunkType  # Type of content
    token_count: int  # Estimated token count
    embedding_id: Optional[str] = None  # Qdrant point ID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### ChatSession
Temporary interaction context between user and RAG system.

```python
class ChatSession(BaseModel):
    id: str  # Session identifier
    created_at: datetime
    last_activity: datetime
    message_count: int  # Number of messages in session
    ip_address: str  # Client IP (hashed for privacy)
    user_agent_hash: str  # Browser fingerprint (hashed)
    is_active: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### QueryLog
Anonymous analytics for query patterns and system performance.

```python
class QueryLog(BaseModel):
    id: str  # UUID
    query_hash: str  # Hash of question for deduplication
    question_length: int  # Character count of question
    context_provided: bool  # Whether user highlighted text
    response_length: int  # Character count of response
    sources_count: int  # Number of content chunks used
    response_time_ms: int  # Total response time
    timestamp: datetime
    date_bucket: str  # YYYY-MM-DD for aggregation
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### ChatMessage
Individual message in chat conversation.

```python
class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    id: str  # Unique message ID
    session_id: str  # Reference to ChatSession
    message_type: MessageType
    content: str  # Message content
    timestamp: datetime
    sources: Optional[List[str]] = None  # Source file references
    context_chunks: Optional[List[str]] = None  # Highlighted text IDs
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## Database Schema (Neon Postgres)

### Tables

```sql
-- Content chunks with metadata
CREATE TABLE content_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL CHECK (length(content) BETWEEN 500 AND 1000),
    source_file VARCHAR(255) NOT NULL,
    chapter VARCHAR(50) NOT NULL,
    section VARCHAR(100),
    chunk_index INTEGER NOT NULL,
    chunk_type VARCHAR(20) NOT NULL DEFAULT 'paragraph',
    token_count INTEGER NOT NULL CHECK (token_count > 0),
    embedding_id VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_chunk_type CHECK (chunk_type IN ('paragraph', 'section', 'code', 'list'))
);

-- Chat sessions for analytics
CREATE TABLE chat_sessions (
    id VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_count INTEGER DEFAULT 0 CHECK (message_count >= 0),
    ip_address INET NOT NULL,
    user_agent_hash VARCHAR(64) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Query logs for analytics
CREATE TABLE query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash VARCHAR(64) NOT NULL,
    question_length INTEGER NOT NULL CHECK (question_length > 0),
    context_provided BOOLEAN DEFAULT FALSE,
    response_length INTEGER NOT NULL CHECK (response_length >= 0),
    sources_count INTEGER DEFAULT 0 CHECK (sources_count >= 0),
    response_time_ms INTEGER NOT NULL CHECK (response_time_ms >= 0),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_bucket VARCHAR(10) NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_content_chunks_source_file ON content_chunks(source_file);
CREATE INDEX idx_content_chunks_chapter ON content_chunks(chapter);
CREATE INDEX idx_chat_sessions_created_at ON chat_sessions(created_at);
CREATE INDEX idx_query_logs_timestamp ON query_logs(timestamp);
CREATE INDEX idx_query_logs_date_bucket ON query_logs(date_bucket);
```

## Vector Schema (Qdrant)

### Collection Configuration

```python
from qdrant_client.models import Distance, VectorParams, PayloadSchema, PayloadSchemaType

collection_config = {
    "vectors": VectorParams(
        size=768,  # Gemini embedding dimensions
        distance=Distance.COSINE
    ),
    "payload_schema": {
        "content": PayloadSchemaType.TEXT,
        "source_file": PayloadSchemaType.TEXT,
        "chapter": PayloadSchemaType.TEXT,
        "section": PayloadSchemaType.TEXT,
        "chunk_index": PayloadSchemaType.INTEGER,
        "chunk_type": PayloadSchemaType.KEYWORD,
        "token_count": PayloadSchemaType.INTEGER,
        "created_at": PayloadSchemaType.DATETIME
    }
}
```

### Point Structure

```python
class VectorPoint(BaseModel):
    id: str  # Unique point identifier
    vector: List[float]  # 768-dimensional embedding
    payload: dict  # ContentChunk metadata
    
    example = {
        "id": "chunk_123_hash",
        "vector": [0.1, 0.2, ...],  # 768 floats
        "payload": {
            "content": "Zero Moment Point (ZMP) is...",
            "source_file": "03-humanoid-design/04-balance-gait.mdx",
            "chapter": "03-humanoid-design",
            "section": "04-balance-gait",
            "chunk_index": 5,
            "chunk_type": "paragraph",
            "token_count": 156,
            "created_at": "2025-12-11T10:00:00Z"
        }
    }
```

## API Data Transfer Objects

### WebSocket Messages

```python
class WebSocketMessage(BaseModel):
    type: str  # "question", "response_start", "response_chunk", "response_end", "error"
    data: dict
    timestamp: Optional[datetime] = None

class QuestionMessage(BaseModel):
    question: str
    context_chunks: Optional[List[str]] = None  # Highlighted text
    session_id: Optional[str] = None

class ResponseStartMessage(BaseModel):
    query_id: str  # Unique query identifier
    estimated_duration: Optional[int] = None  # ms

class ResponseChunkMessage(BaseModel):
    content: str  # Partial response content
    is_complete: bool = False
    sources: Optional[List[dict]] = None  # Source references

class ResponseEndMessage(BaseModel):
    query_id: str
    response_time_ms: int
    total_tokens: int
    sources_used: int
```

### HTTP API Models

```python
class HealthResponse(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    version: str
    uptime_seconds: int
    active_connections: int

class IngestionRequest(BaseModel):
    force: bool = False  # Re-ingest all content
    file_patterns: Optional[List[str]] = None  # Specific files to process

class IngestionResponse(BaseModel):
    status: str  # "started", "completed", "failed"
    files_processed: int
    chunks_created: int
    duration_ms: int
    errors: List[str] = []
```

## State Transitions

### Content Lifecycle

```
[New File] → [Parsed] → [Chunked] → [Embedded] → [Stored]
     ↓           ↓          ↓           ↓          ↓
   Monitor    Validate   Split      Generate   Index
```

### Chat Session Flow

```
[Connect] → [Question] → [Retrieve] → [Generate] → [Stream] → [Complete]
     ↓           ↓          ↓           ↓          ↓          ↓
   Create    Parse      Search      LLM       Send      Log
```

### Error Recovery

```
[Error] → [Retry] → [Fallback] → [Notify]
    ↓        ↓         ↓          ↓
  Log     Wait     Cache     User
```

## Validation Rules

### Content Validation
- Content length: 500-1000 characters
- Token count: > 0
- Source file: Must exist in docs/ directory
- Chapter: Must match directory structure

### Query Validation
- Question length: 1-1000 characters
- Context chunks: Maximum 5 highlighted sections
- Rate limit: 10 requests per minute per IP

### Response Validation
- Response time: < 2000ms (95th percentile)
- Source citations: At least 1 source per response
- Content source: Must be from existing book content

## Privacy and Security

### Data Anonymization
- IP addresses: Hashed with salt
- User agents: Hashed, not stored raw
- Questions: No PII detection required (anonymous)
- Sessions: Expire after 24 hours of inactivity

### Access Control
- No authentication required
- Rate limiting by IP address
- Input sanitization for all user inputs
- CORS restricted to configured domains

## Performance Considerations

### Indexing Strategy
- Qdrant HNSW index for fast approximate search
- PostgreSQL indexes on frequently queried fields
- Redis cache for repeated queries

### Caching Layers
- Embedding cache: Redis with 1-hour TTL
- Response cache: Redis with 30-minute TTL
- Content cache: In-memory for hot documents

### Monitoring Metrics
- Query latency: p50, p95, p99
- Cache hit rates: Embeddings, responses
- Error rates: By type and endpoint
- Resource usage: Memory, CPU, connections