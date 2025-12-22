# Data Model: Chatbot Agent Integration

## Overview

This document defines the data models for the chatbot agent integration, building upon the existing retrieval system models and extending them for agent-specific functionality.

## Core Entities

### 1. ChatSession

Represents a conversation session between user and agent.

```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class ChatSession(BaseModel):
    session_id: str = str(uuid.uuid4())
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = []  # List of {role: "user|assistant", content: str, timestamp: datetime}
    metadata: Dict[str, Any] = {}
```

### 2. AgentQuery (extends existing Query)

Query with agent-specific context and options.

```python
from ..models.query_models import Query, QueryContext

class AgentQuery(BaseModel):
    base_query: Query  # Inherit from existing Query model
    session_id: Optional[str] = None
    agent_instructions: Optional[str] = "You are a robotics expert assistant. Answer questions based on the provided context from robotics books. Always cite your sources."
    require_sources: bool = True
    max_tokens: Optional[int] = 1000
    temperature: float = 0.7
    conversation_context: Optional[QueryContext] = None
```

### 3. RetrievedContent (existing model - referenced)

The existing model from the retrieval system:

```python
from pydantic import BaseModel
from typing import Optional

class RetrievedContent(BaseModel):
    id: str
    chunk_id: str
    content: str
    source_file: str
    source_location: str
    relevance_score: float
    metadata: Optional[dict] = None
```

### 4. AgentResponse

Response from the agent with source attribution.

```python
from typing import List
from datetime import datetime

class AgentResponse(BaseModel):
    session_id: str
    query: str
    response: str
    sources: List[RetrievedContent] = []
    conversation_turn: int
    timestamp: datetime
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None  # Processing time in seconds
    has_relevant_content: bool = True
    error: Optional[str] = None
```

### 5. AgentToolResult

Result from agent tools (like retrieval).

```python
class AgentToolResult(BaseModel):
    tool_name: str
    success: bool
    content: List[RetrievedContent] = []
    error: Optional[str] = None
    execution_time: Optional[float] = None
```

### 6. AgentConfig

Configuration for the agent behavior.

```python
class AgentConfig(BaseModel):
    model_name: str = "gemini-2.5-flash"  # Default model
    temperature: float = 0.7
    max_tokens: int = 1000
    top_k: int = 5  # Number of results to retrieve
    min_relevance_score: float = 0.5
    enable_tracing: bool = False
    timeout_seconds: int = 30
    fallback_response: str = "I couldn't find relevant information to answer your question. Please try rephrasing or ask about a different topic related to robotics."
```

## API Request/Response Models

### 7. ChatRequest

Request model for chat interactions.

```python
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # If not provided, creates new session
    require_sources: bool = True
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
```

### 8. ChatResponse

Response model for chat interactions.

```python
class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: List[RetrievedContent]
    conversation_turn: int
    has_relevant_content: bool
    timestamp: datetime
```

### 9. StreamingChatResponse

For streaming responses (if implemented).

```python
class StreamingChatResponse(BaseModel):
    session_id: str
    chunk: str
    is_final: bool
    sources: Optional[List[RetrievedContent]] = None
    timestamp: datetime
```

## Data Flow

### Standard Chat Flow
1. User sends `ChatRequest` with message and optional session_id
2. System creates/loads `ChatSession` with conversation history
3. System creates `AgentQuery` with context from session
4. System retrieves `RetrievedContent` using existing retrieval service
5. Agent generates response based on retrieved content
6. System creates `AgentResponse` with sources and metadata
7. System returns `ChatResponse` to user
8. System updates `ChatSession` with new conversation turn

### Error Flow
1. If no relevant content found, agent uses fallback response
2. If agent unavailable, system returns error response
3. If retrieval fails, system returns error with appropriate message

## Relationships

- `ChatSession` contains multiple conversation turns
- `AgentQuery` references `QueryContext` from existing system
- `AgentResponse` contains multiple `RetrievedContent` items
- `ChatRequest` maps to `ChatResponse`

## Validation Rules

1. **Query Validation**: All queries must be at least 3 characters
2. **Session Validation**: Session ID must be valid UUID format
3. **Content Validation**: Retrieved content must meet minimum relevance score
4. **Response Validation**: Agent responses must be grounded in retrieved content
5. **Context Validation**: Conversation history must not exceed size limits

## Storage Considerations

1. **Session Storage**: Chat sessions may be stored in memory or Redis for short-term, database for long-term
2. **History Limits**: Conversation history should be limited to prevent excessive context
3. **Caching**: Retrieved content should leverage existing caching mechanisms
4. **Metadata**: Additional metadata should be stored for analytics and debugging

## Extension Points

1. **Multi-modal Support**: Future support for images, code blocks
2. **Function Calling**: Integration with robotics-specific tools/functions
3. **Personalization**: User-specific preferences and context
4. **Analytics**: Response quality and user satisfaction tracking