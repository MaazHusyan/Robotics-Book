# API Contract: Chatbot Agent Integration

## Overview

This document defines the API contracts for the chatbot agent integration, specifying the endpoints, request/response schemas, and behavior for the agent-powered chat functionality.

## Base URL

All API endpoints are relative to:
```
http://localhost:8000/api/v1
```

## Authentication

No authentication required for this initial implementation. In production, API keys or other authentication mechanisms would be implemented.

## Common Headers

All requests and responses use:
- `Content-Type: application/json`
- `Accept: application/json`

## Endpoints

### 1. Chat Message Endpoint

#### POST `/chat`

Send a message to the chatbot agent and receive a response.

##### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "message": "What is forward kinematics?",
  "session_id": "session-12345",
  "require_sources": true,
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "message": {
      "type": "string",
      "description": "The user's message to the chatbot",
      "minLength": 1,
      "maxLength": 10000
    },
    "session_id": {
      "type": ["string", "null"],
      "description": "Session identifier to maintain conversation context. If null, a new session is created.",
      "pattern": "^[a-zA-Z0-9-_]+$"
    },
    "require_sources": {
      "type": "boolean",
      "description": "Whether to require source citations in the response",
      "default": true
    },
    "temperature": {
      "type": "number",
      "description": "Controls randomness in response (0.0-1.0)",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.7
    },
    "max_tokens": {
      "type": "integer",
      "description": "Maximum number of tokens in the response",
      "minimum": 1,
      "maximum": 4000,
      "default": 1000
    }
  },
  "required": ["message"]
}
```

##### Response

**Success Response (200 OK):**
```json
{
  "session_id": "session-12345",
  "response": "Forward kinematics is the process of determining the position and orientation of the end-effector of a robotic manipulator based on the given joint angles...",
  "sources": [
    {
      "id": "doc123",
      "chunk_id": "chunk456",
      "content": "Robot kinematics is the study of motion in robotic systems...",
      "source_file": "robotics_book_chapter_3.pdf",
      "source_location": "Chapter 3, Section 2.1",
      "relevance_score": 0.87
    }
  ],
  "conversation_turn": 1,
  "has_relevant_content": true,
  "timestamp": "2025-12-18T10:30:00.123456"
}
```

**Response Schema:**
```json
{
  "type": "object",
  "properties": {
    "session_id": {
      "type": "string",
      "description": "The session identifier used for this conversation"
    },
    "response": {
      "type": "string",
      "description": "The agent's response to the user's message"
    },
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "chunk_id": {"type": "string"},
          "content": {"type": "string"},
          "source_file": {"type": "string"},
          "source_location": {"type": "string"},
          "relevance_score": {"type": "number"}
        },
        "required": ["id", "chunk_id", "content", "source_file", "source_location", "relevance_score"]
      },
      "description": "List of sources used to generate the response"
    },
    "conversation_turn": {
      "type": "integer",
      "description": "The turn number in the conversation (1-indexed)"
    },
    "has_relevant_content": {
      "type": "boolean",
      "description": "Whether relevant content was found to answer the question"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp of the response"
    }
  },
  "required": ["session_id", "response", "sources", "conversation_turn", "has_relevant_content", "timestamp"]
}
```

**Error Responses:**

- **400 Bad Request**: Invalid request parameters
  ```json
  {
    "error": "Bad Request",
    "message": "Message field is required and must be at least 1 character long"
  }
  ```

- **429 Too Many Requests**: Rate limit exceeded
  ```json
  {
    "error": "Too Many Requests",
    "message": "Rate limit exceeded"
  }
  ```

- **500 Internal Server Error**: Server error during processing
  ```json
  {
    "error": "Internal Server Error",
    "message": "Internal server error during chat processing"
  }
  ```

### 2. Session Management Endpoints (Future Extension)

#### GET `/session/{session_id}`

Get session details and conversation history.

**Response (200 OK):**
```json
{
  "session_id": "session-12345",
  "created_at": "2025-12-18T10:00:00.123456",
  "updated_at": "2025-12-18T10:30:00.123456",
  "conversation_history": [
    {
      "role": "user",
      "content": "What is forward kinematics?",
      "timestamp": "2025-12-18T10:25:00.123456"
    },
    {
      "role": "assistant",
      "content": "Forward kinematics is the process...",
      "sources": [...],
      "timestamp": "2025-12-18T10:25:01.123456"
    }
  ]
}
```

#### DELETE `/session/{session_id}`

End and clear a conversation session.

**Response (200 OK):**
```json
{
  "message": "Session cleared successfully",
  "session_id": "session-12345"
}
```

## Error Handling

### Standard Error Response Format
```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "details": {
    "field": "specific field that caused the error (if applicable)"
  }
}
```

### Common Error Codes

| Code | Description | Example |
|------|-------------|---------|
| 400 | Bad Request | Invalid input parameters |
| 404 | Not Found | Session ID doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Agent or retrieval service unavailable |

## Performance Requirements

- **Response Time**: <5 seconds for 95th percentile
- **Availability**: 99.9% uptime
- **Throughput**: Support 100 concurrent sessions
- **Latency**: <2 seconds for simple queries

## Security Considerations

- Input validation to prevent injection attacks
- Rate limiting to prevent abuse
- Content filtering to prevent inappropriate responses
- Proper error message sanitization to avoid information leakage

## Monitoring and Logging

All API calls should be logged with:
- Request ID for traceability
- Timestamp
- Session ID
- Request parameters (sanitized)
- Response time
- Error codes (if applicable)

## Versioning

This contract follows the v1 API version. Future breaking changes will increment the version number (v2, v3, etc.).

## Examples

### Example 1: Initial Message (New Session)
```
POST /api/v1/chat
{
  "message": "What is robot kinematics?",
  "session_id": null
}
```

### Example 2: Follow-up Message (Existing Session)
```
POST /api/v1/chat
{
  "message": "Can you explain inverse kinematics too?",
  "session_id": "session-12345",
  "require_sources": true
}
```

### Example 3: Message with Custom Parameters
```
POST /api/v1/chat
{
  "message": "How do I control a robotic arm?",
  "session_id": "session-67890",
  "temperature": 0.5,
  "max_tokens": 500
}
```