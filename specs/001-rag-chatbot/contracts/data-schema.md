# Data Schema: Database and Vector Store

**Version**: 1.0.0  
**Created**: 2025-12-10  
**Purpose**: Schema definitions for Neon Postgres and Qdrant Cloud

## Neon Postgres Schema

### content_chunks Table

```sql
CREATE TABLE content_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL CHECK (length(content) BETWEEN 500 AND 1000),
    source_file VARCHAR(255) NOT NULL,
    chapter VARCHAR(50) NOT NULL,
    section VARCHAR(100),
    chunk_index INTEGER NOT NULL,
    token_count INTEGER NOT NULL CHECK (token_count > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_content_chunks_source ON content_chunks(source_file);
CREATE INDEX idx_content_chunks_chapter ON content_chunks(chapter);
```

### chat_sessions Table

```sql
CREATE TABLE chat_sessions (
    id VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_count INTEGER DEFAULT 0 CHECK (message_count >= 0),
    ip_address INET NOT NULL,
    user_agent_hash VARCHAR(64) NOT NULL
);

CREATE INDEX idx_chat_sessions_ip ON chat_sessions(ip_address);
CREATE INDEX idx_chat_sessions_activity ON chat_sessions(last_activity);
```

### query_logs Table

```sql
CREATE TABLE query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash VARCHAR(64) NOT NULL,
    question_length INTEGER NOT NULL CHECK (question_length > 0),
    context_provided BOOLEAN DEFAULT FALSE,
    response_length INTEGER NOT NULL CHECK (response_length >= 0),
    sources_count INTEGER DEFAULT 0 CHECK (sources_count >= 0),
    response_time_ms INTEGER NOT NULL CHECK (response_time_ms >= 0),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_bucket VARCHAR(10) NOT NULL -- YYYY-MM-DD format
);

CREATE INDEX idx_query_logs_timestamp ON query_logs(timestamp);
CREATE INDEX idx_query_logs_bucket ON query_logs(date_bucket);
CREATE UNIQUE INDEX idx_query_logs_hash ON query_logs(query_hash, date_bucket);
```

### system_metrics Table

```sql
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,3) NOT NULL,
    metric_unit VARCHAR(20),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp);
```

## Qdrant Cloud Schema

### content_vectors Collection

```json
{
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  },
  "payload_schema": {
    "chunk_id": "keyword",
    "source_file": "keyword", 
    "chapter": "keyword",
    "section": "keyword",
    "chunk_index": "integer",
    "token_count": "integer"
  }
}
```

### Vector Payload Structure

```json
{
  "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
  "source_file": "docs/03-humanoid-design/zmp-locomotion.mdx",
  "chapter": "03-humanoid-design", 
  "section": "03-zmp-locomotion",
  "chunk_index": 5,
  "token_count": 127
}
```

## Data Relationships

### Foreign Key Relationships

```sql
-- Content chunks reference vector embeddings via chunk_id
-- Query logs reference chat sessions via session_id (denormalized for performance)
-- System metrics are independent time-series data
```

## Constraints and Validation

### Content Constraints

- Content length strictly 500-1000 characters
- Source files must exist in docs/ directory
- Chapter names follow pattern: ##-chapter-name
- No duplicate chunk_id values

### Session Constraints

- Session ID format: [a-zA-Z0-9\-]{1,64}
- IP address validation for IPv4/IPv6
- User agent hash: SHA-256 of user agent string
- Sessions expire after 30 minutes inactivity

### Query Log Constraints

- Query hash: SHA-256 of question + date bucket
- Question length: 1-280 characters
- Response time recorded in milliseconds
- Daily aggregation via date_bucket field

## Indexing Strategy

### Postgres Indexes

- **content_chunks**: Source file and chapter for content management
- **chat_sessions**: IP and activity for session cleanup
- **query_logs**: Timestamp and bucket for analytics queries
- **system_metrics**: Name and time for performance monitoring

### Qdrant Indexing

- **HNSW algorithm** for approximate nearest neighbor search
- **Cosine similarity** for semantic search
- **Payload indexing** on source_file and chapter for filtering
- **Shard count**: 1 (appropriate for free tier)

## Data Migration

### Version Control

```sql
-- Schema version tracking
CREATE TABLE schema_versions (
    version VARCHAR(10) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT
);

INSERT INTO schema_versions (version, description) 
VALUES ('1.0.0', 'Initial RAG chatbot schema');
```

### Backup Strategy

- Daily automated backups via Neon
- Point-in-time recovery for 30 days
- Export capability for content chunks
- Vector backup through Qdrant snapshots