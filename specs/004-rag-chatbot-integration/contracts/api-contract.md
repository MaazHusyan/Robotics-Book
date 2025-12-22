# API Contract: RAG Chatbot Integration (Updated)

## Overview
The RAG Chatbot API provides endpoints for interacting with a robotics book content chatbot. The API adapts the agent implementation from `@References/rag_agent.py` and wraps it in FastAPI endpoints. The system uses Qdrant retrieval patterns from `@References/qdrant_retrieve.py` and model configuration from `@References/gemini_model.py`.

## Base URL
`http://localhost:8000/api/v1` (or configured base URL)

## Authentication
None required for basic functionality (may be added in future iterations)

## Endpoints

### POST /chat
Send a message to the chatbot and receive a response.

#### Request
```json
{
  "message": "What is humanoid robotics?",
  "session_id": "optional-session-id",
  "require_sources": true,
  "temperature": 0.7,
  "max_tokens": 1000
}
```

#### Request Parameters
- `message` (string, required): The user's message/query. Must be 1-10,000 characters.
- `session_id` (string, optional): Session identifier to maintain conversation context. If not provided, a new session is created.
- `require_sources` (boolean, optional): Whether to require source citations in response. Default: true.
- `temperature` (number, optional): Controls randomness in response (0.0-1.0). Default: 0.7.
- `max_tokens` (integer, optional): Maximum number of tokens in response. Default: 1000.

#### Response (200 OK)
```json
{
  "session_id": "session-123",
  "response": "Humanoid robotics is a branch of robotics focused on creating robots with human-like characteristics...",
  "sources": [
    {
      "id": "chunk-1",
      "content": "Humanoid robots are robots that resemble the human body structure...",
      "source_file": "robotics_book_chapter_3.md",
      "source_location": "Chapter 3, Section 2",
      "relevance_score": 0.87
    }
  ],
  "conversation_turn": 1,
  "has_relevant_content": true,
  "timestamp": "2025-12-20T10:30:00Z"
}
```

#### Response Fields
- `session_id` (string): The session identifier (new or existing)
- `response` (string): The chatbot's response to the user's message
- `sources` (array): List of source documents used to generate the response
- `conversation_turn` (integer): The turn number in the conversation (1-indexed)
- `has_relevant_content` (boolean): Whether relevant content was found in the book
- `timestamp` (string): ISO 8601 timestamp of the response

#### Error Responses
- `400 Bad Request`: Invalid request parameters
  ```json
  {
    "detail": "Message field is required and must be at least 1 character long"
  }
  ```

- `500 Internal Server Error`: Server error during processing
  ```json
  {
    "detail": "Internal server error during chat processing"
  }
  ```

### GET /session/{session_id}
Retrieve session details and conversation history.

#### Response (200 OK)
```json
{
  "session_id": "session-123",
  "created_at": "2025-12-20T10:00:00Z",
  "updated_at": "2025-12-20T10:30:00Z",
  "conversation_history": [
    {
      "role": "user",
      "content": "What is humanoid robotics?",
      "timestamp": "2025-12-20T10:25:00Z"
    },
    {
      "role": "assistant",
      "content": "Humanoid robotics is a branch of robotics focused on creating robots with human-like characteristics...",
      "timestamp": "2025-12-20T10:25:05Z",
      "sources": [...],
      "retrieval_error": null,
      "agent_error": null
    }
  ],
  "user_id": "user-123"
}
```

#### Error Responses
- `404 Not Found`: Session not found
  ```json
  {
    "detail": "Session not found"
  }
  ```

- `500 Internal Server Error`: Server error during retrieval
  ```json
  {
    "detail": "Internal server error while retrieving session"
  }
  ```

### DELETE /session/{session_id}
End and clear a conversation session.

#### Response (200 OK)
```json
{
  "message": "Session cleared successfully",
  "session_id": "session-123"
}
```

#### Error Responses
- `404 Not Found`: Session not found
  ```json
  {
    "detail": "Session not found"
  }
  ```

- `500 Internal Server Error`: Server error during clearing
  ```json
  {
    "detail": "Internal server error while clearing session"
  }
  ```

## Data Models

### ChatRequest
Request body for the /chat endpoint.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User's message (1-10,000 chars) |
| session_id | string | No | Session identifier |
| require_sources | boolean | No | Require source citations (default: true) |
| temperature | number | No | Response randomness (0.0-1.0, default: 0.7) |
| max_tokens | integer | No | Max tokens in response (default: 1000) |

### ChatResponse
Response from the /chat endpoint.

| Field | Type | Description |
|-------|------|-------------|
| session_id | string | Session identifier |
| response | string | Chatbot's response |
| sources | array | Source documents used |
| conversation_turn | integer | Turn number in conversation |
| has_relevant_content | boolean | Whether relevant content was found |
| timestamp | string | Response timestamp (ISO 8601) |

### Source Document
Item in the sources array.

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier for content chunk |
| content | string | Content text used |
| source_file | string | Name of source file |
| source_location | string | Location in source (chapter, page, etc.) |
| relevance_score | number | Relevance score (0.0-1.0) |

## Error Handling
- All errors follow the standard FastAPI error format with a "detail" field
- Client errors (4xx) indicate invalid requests
- Server errors (5xx) indicate internal processing issues
- The system should never return fabricated content; if no relevant content is found, it should indicate this clearly (following the pattern from rag_agent.py)

## Performance Requirements
- Response time: <5 seconds for typical queries
- Content retrieval accuracy: >90% for relevant queries
- The system should handle concurrent users appropriately

## Security Considerations
- Input sanitization: Messages are sanitized to prevent injection attacks
- Session ID validation: Format validation to prevent injection
- Rate limiting: Should be implemented at the API gateway level (not in this service)

## Reference File Integration
This API integrates functionality adapted from:
- `@References/rag_agent.py`: Agent execution, tool usage, and conversation handling
- `@References/qdrant_retrieve.py`: Qdrant connection and retrieval patterns
- `@References/gemini_model.py`: Model configuration and execution setup