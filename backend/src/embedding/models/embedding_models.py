from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class EmbeddingVector(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chunk_id: str
    vector: List[float]
    model: str
    dimensionality: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
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