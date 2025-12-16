# Data Model: FastAPI Integration for Robotics Book

## Entities

### APIEndpoint
- **name**: string (the endpoint name/route)
- **path**: string (the URL path pattern)
- **methods**: string[] (HTTP methods supported: GET, POST, etc.)
- **description**: string (human-readable description of the endpoint)
- **request_schema**: object (Pydantic model for request validation)
- **response_schema**: object (Pydantic model for response validation)

### APISession
- **id**: string (UUID for the session)
- **created_at**: datetime (timestamp when session was created)
- **last_access**: datetime (timestamp of last API interaction)
- **user_agent**: string (client information)
- **ip_address**: string (client IP address)
- **request_count**: integer (number of requests in this session)

### APIResponse
- **id**: string (UUID for the response)
- **status_code**: integer (HTTP status code)
- **headers**: object (response headers)
- **body**: object (response content)
- **timestamp**: datetime (when response was generated)
- **request_id**: string (reference to associated request)

### BookContent
- **id**: string (unique identifier for the content)
- **title**: string (title of the content section)
- **content**: string (the actual book content)
- **chapter**: string (chapter identifier)
- **section**: string (section identifier)
- **metadata**: object (additional content metadata)
- **created_at**: datetime (when content was added to the system)
- **updated_at**: datetime (when content was last modified)

### HealthStatus
- **status**: string (overall health status: "healthy", "degraded", "unhealthy")
- **timestamp**: datetime (when the status was checked)
- **dependencies**: object (status of various system dependencies)

### APIStatus
- **version**: string (API version)
- **uptime**: string (API uptime information)
- **requests_processed**: integer (total number of requests processed)
- **environment**: string (environment name: dev, test, prod)

## Relationships
- One APISession can have many APIResponse records (1:N)
- APIEndpoint defines the structure for APIResponse (1:N)

## Validation Rules
- APIEndpoint.path must follow FastAPI path format with proper parameter syntax
- APISession.id must be a valid UUID
- APIResponse.status_code must be a valid HTTP status code
- Timestamps must be in ISO 8601 format
- BookContent.id must be unique within the system

## State Transitions
APISession: [CREATED] → [ACTIVE] → [EXPIRED/INACTIVE]

## Pydantic Models
```python
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
```