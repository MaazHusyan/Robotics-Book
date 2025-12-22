# API Documentation: Chatbot Agent Integration

## Overview
This document provides detailed information about the API endpoints for the Chatbot Agent Integration feature. The API allows users to interact with a robotics expert agent that retrieves relevant content from robotics books and provides accurate, source-cited responses.

## Base URL
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

### 1. Chat Endpoint
#### POST `/chat`

Send a message to the chatbot agent and receive a response.

##### Request Headers
```
Content-Type: application/json
```

##### Request Body
```json
{
  "message": "What is forward kinematics?",
  "session_id": "session-12345",
  "require_sources": true,
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Request Fields:**
- `message` (string, required): The user's message to the chatbot. Minimum length: 1 character. Maximum length: 10,000 characters.
- `session_id` (string or null, optional): Session identifier to maintain conversation context. If null, a new session is created.
- `require_sources` (boolean, optional): Whether to require source citations in the response. Default: true.
- `temperature` (number, optional): Controls randomness in response (0.0-1.0). Default: 0.7.
- `max_tokens` (integer, optional): Maximum number of tokens in the response. Minimum: 1. Default: 1000.

##### Success Response (200 OK)
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

**Response Fields:**
- `session_id` (string): The session identifier used for this conversation
- `response` (string): The agent's response to the user's message
- `sources` (array): List of sources used to generate the response
  - `id` (string): Document ID
  - `chunk_id` (string): Chunk identifier within the document
  - `content` (string): Content snippet
  - `source_file` (string): Source file name
  - `source_location` (string): Location within the source (e.g., chapter, section)
  - `relevance_score` (number): Relevance score (0.0-1.0)
- `conversation_turn` (integer): The turn number in the conversation (1-indexed)
- `has_relevant_content` (boolean): Whether relevant content was found to answer the question
- `timestamp` (string): ISO 8601 formatted timestamp

##### Error Responses

**400 Bad Request**
```json
{
  "detail": "Message field is required and must be at least 1 character long"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error during chat processing"
}
```

### 2. Session Management Endpoints

#### GET `/session/{session_id}`

Get session details and conversation history.

##### Path Parameters
- `session_id` (string): The session identifier to retrieve

##### Success Response (200 OK)
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
  ],
  "user_id": null
}
```

#### DELETE `/session/{session_id}`

End and clear a conversation session.

##### Path Parameters
- `session_id` (string): The session identifier to clear

##### Success Response (200 OK)
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
  "detail": "Human-readable error message"
}
```

### Common Error Codes
| Code | Description | Example |
|------|-------------|---------|
| 400 | Bad Request | Invalid input parameters |
| 404 | Not Found | Session ID doesn't exist |
| 422 | Unprocessable Entity | Validation errors |
| 500 | Internal Server Error | Unexpected server error |

## Performance Requirements
- Response time: <5 seconds for 95th percentile
- Availability: 99.9% uptime
- Throughput: Support 100 concurrent sessions

## Security Considerations
- Input validation to prevent injection attacks
- Rate limiting to prevent abuse
- Content filtering to prevent inappropriate responses
- Proper error message sanitization to avoid information leakage

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

## Testing
The API endpoints are covered by both unit and integration tests:
- Unit tests: `backend/tests/unit/test_agent_service.py`
- Integration tests: `backend/tests/integration/test_agent_endpoint.py`