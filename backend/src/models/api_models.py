from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class APIEndpoint(BaseModel):
    name: str
    path: str
    methods: List[str]
    description: str
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None


class APISession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    last_access: datetime = Field(default_factory=datetime.now)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    request_count: int = 0


class APIResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status_code: int
    headers: Dict[str, str] = {}
    body: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None


class BookContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    chapter: str
    section: str
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class HealthStatus(BaseModel):
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    dependencies: Dict[str, str] = {}


class APIStatus(BaseModel):
    version: str
    uptime: str
    requests_processed: int
    environment: str