from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class ChunkType(str, Enum):
    PARAGRAPH = "paragraph"
    SECTION = "section"
    CODE = "code"
    LIST = "list"


class ContentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(..., min_length=500, max_length=1000)
    source_file: str = Field(..., description="Relative path to MDX file")
    chapter: str = Field(..., description="Chapter directory name")
    section: str = Field(..., description="Section name without extension")
    chunk_index: int = Field(..., ge=0, description="Order within file")
    chunk_type: ChunkType = Field(default=ChunkType.PARAGRAPH)
    token_count: int = Field(..., gt=0, description="Estimated token count")
    embedding_id: Optional[str] = Field(None, description="Qdrant point ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ChatSession(BaseModel):
    id: str = Field(..., description="Session identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = Field(
        default=0, ge=0, description="Number of messages in session"
    )
    ip_address: str = Field(..., description="Client IP (hashed for privacy)")
    user_agent_hash: str = Field(..., description="Browser fingerprint (hashed)")
    is_active: bool = Field(default=True)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class QueryLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query_hash: str = Field(..., description="Hash of question for deduplication")
    question_length: int = Field(..., gt=0, description="Character count of question")
    context_provided: bool = Field(
        default=False, description="Whether user highlighted text"
    )
    response_length: int = Field(..., ge=0, description="Character count of response")
    sources_count: int = Field(
        default=0, ge=0, description="Number of content chunks used"
    )
    response_time_ms: int = Field(..., ge=0, description="Total response time")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    date_bucket: str = Field(..., description="YYYY-MM-DD for aggregation")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(..., description="Reference to ChatSession")
    message_type: MessageType = Field(..., description="Type of message")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sources: Optional[List[str]] = Field(None, description="Source file references")
    context_chunks: Optional[List[str]] = Field(
        None, description="Highlighted text IDs"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
