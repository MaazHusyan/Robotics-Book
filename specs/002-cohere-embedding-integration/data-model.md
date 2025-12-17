# Data Model: Cohere Embedding Model Integration

## Entities

### ContentChunk
- **id**: string (unique identifier for the content chunk)
- **text**: string (the actual text content to be embedded)
- **source_file**: string (reference to the original book content file)
- **source_location**: string (location within the source, e.g., "Chapter 3, Section 2")
- **metadata**: object (additional metadata like chapter, section, tags)
- **created_at**: datetime (timestamp when chunk was created)
- **updated_at**: datetime (timestamp when chunk was last modified)

### EmbeddingVector
- **id**: string (unique identifier for the embedding)
- **chunk_id**: string (reference to the source content chunk)
- **vector**: float[] (the numerical vector representation from Cohere)
- **model**: string (the model used to generate the embedding, e.g., "embed-english-v3.0")
- **dimensionality**: integer (number of dimensions in the vector)
- **created_at**: datetime (timestamp when embedding was generated)

### EmbeddingJob
- **id**: string (unique identifier for the batch job)
- **status**: string (status of the job: "pending", "in_progress", "completed", "failed")
- **total_chunks**: integer (total number of chunks to process)
- **processed_chunks**: integer (number of chunks processed so far)
- **failed_chunks**: integer (number of chunks that failed processing)
- **model**: string (the embedding model to use)
- **created_at**: datetime (timestamp when job was created)
- **started_at**: datetime (timestamp when job started processing)
- **completed_at**: datetime (timestamp when job was completed)
- **error_log**: string[] (list of errors encountered during processing)

### EmbeddingConfig
- **model**: string (the Cohere model to use, default: "embed-english-v3.0")
- **input_type**: string (type of input: "search_document", "search_query", etc.)
- **truncate**: string (how to handle long inputs: "START", "END", "NONE")
- **batch_size**: integer (number of chunks to process in each API call, default: 96)
- **rate_limit_requests**: integer (max requests per minute, default: 100)
- **rate_limit_seconds**: integer (time window in seconds, default: 60)
- **retry_attempts**: integer (number of retry attempts for failed API calls, default: 3)

## Relationships
- One EmbeddingJob can process many ContentChunk records (1:N)
- One ContentChunk can have one EmbeddingVector (1:1)
- EmbeddingJob contains many EmbeddingVector records (1:N)

## Validation Rules
- ContentChunk.text must not exceed 4000 tokens for Cohere API limits
- EmbeddingVector.vector must have consistent dimensionality based on the model used
- EmbeddingJob.status must be one of the allowed status values
- EmbeddingConfig.batch_size must be between 1 and 96 (Cohere API limit)
- Timestamps must be in ISO 8601 format

## State Transitions
ContentChunk: [CREATED] → [EMBEDDING_QUEUED] → [EMBEDDING_IN_PROGRESS] → [EMBEDDED/SKIPPED/FAILED]

EmbeddingJob: [CREATED] → [QUEUED] → [IN_PROGRESS] → [COMPLETED/FAILED]

## Pydantic Models
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ContentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    source_file: str
    source_location: str
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class EmbeddingVector(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chunk_id: str
    vector: List[float]
    model: str
    dimensionality: int
    created_at: datetime = Field(default_factory=datetime.now)

class EmbeddingJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str
    total_chunks: int
    processed_chunks: int = 0
    failed_chunks: int = 0
    model: str
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_log: List[str] = []

class EmbeddingConfig(BaseModel):
    model: str = "embed-english-v3.0"
    input_type: str = "search_document"
    truncate: str = "END"
    batch_size: int = 96
    rate_limit_requests: int = 100
    rate_limit_seconds: int = 60
    retry_attempts: int = 3
```