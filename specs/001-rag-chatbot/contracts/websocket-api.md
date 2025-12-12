# WebSocket API Contract

**Version**: 1.0.0  
**Date**: 2025-12-11  
**Purpose**: Real-time chat interface for RAG tutor

## Connection

### Endpoint
```
WSS /ws/chat
```

### Connection Headers
```http
Sec-WebSocket-Protocol: chat-v1
Origin: https://username.github.io
```

### Connection Flow
1. Client connects to WebSocket endpoint
2. Server accepts connection and sends welcome message
3. Client sends questions, server streams responses
4. Connection remains open for multiple questions

## Message Format

### Base Message Structure
```json
{
  "type": "string",
  "data": {},
  "timestamp": "2025-12-11T10:00:00Z"
}
```

### Client Messages

#### Question
```json
{
  "type": "question",
  "data": {
    "question": "What is Zero Moment Point?",
    "context_chunks": ["chunk_123", "chunk_456"],
    "session_id": "session_abc123"
  },
  "timestamp": "2025-12-11T10:00:00Z"
}
```

**Validation Rules**:
- `question`: Required, 1-1000 characters
- `context_chunks`: Optional, max 5 items
- `session_id`: Optional, auto-generated if missing

#### Ping
```json
{
  "type": "ping",
  "data": {},
  "timestamp": "2025-12-11T10:00:00Z"
}
```

### Server Messages

#### Welcome (Connection Established)
```json
{
  "type": "welcome",
  "data": {
    "session_id": "session_abc123",
    "server_version": "1.0.0",
    "features": ["text_selection", "streaming", "source_citation"]
  },
  "timestamp": "2025-12-11T10:00:00Z"
}
```

#### Response Start
```json
{
  "type": "response_start",
  "data": {
    "query_id": "query_xyz789",
    "estimated_duration": 1500
  },
  "timestamp": "2025-12-11T10:00:00Z"
}
```

#### Response Chunk
```json
{
  "type": "response_chunk",
  "data": {
    "content": "Zero Moment Point (ZMP) is a crucial concept...",
    "is_complete": false,
    "sources": [
      {
        "file": "03-humanoid-design/04-balance-gait.mdx",
        "chapter": "03-humanoid-design",
        "section": "04-balance-gait"
      }
    ]
  },
  "timestamp": "2025-12-11T10:00:01Z"
}
```

#### Response End
```json
{
  "type": "response_end",
  "data": {
    "query_id": "query_xyz789",
    "response_time_ms": 1450,
    "total_tokens": 156,
    "sources_used": 2
  },
  "timestamp": "2025-12-11T10:00:02Z"
}
```

#### Error
```json
{
  "type": "error",
  "data": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please wait before asking another question.",
    "retry_after": 30
  },
  "timestamp": "2025-12-11T10:00:00Z"
}
```

#### Pong
```json
{
  "type": "pong",
  "data": {},
  "timestamp": "2025-12-11T10:00:00Z"
}
```

## Error Codes

| Code | Description | Retry |
|------|-------------|-------|
| `INVALID_MESSAGE` | Malformed JSON or missing required fields | No |
| `QUESTION_TOO_LONG` | Question exceeds 1000 characters | No |
| `RATE_LIMIT_EXCEEDED` | Too many requests from IP | Yes (after retry_after) |
| `CONTEXT_NOT_FOUND` | Referenced context chunks don't exist | No |
| `SERVICE_UNAVAILABLE` | Backend services temporarily down | Yes (exponential backoff) |
| `CONTENT_NOT_FOUND` | No relevant content found for question | No |
| `INVALID_SESSION` | Session ID format invalid | No |

## Rate Limiting

### Per-IP Limits
- 10 questions per minute
- 50 questions per hour
- 200 questions per day

### Per-Connection Limits
- 1 concurrent question processing
- Maximum 100 messages per connection
- Connection timeout after 30 minutes inactivity

## Security

### CORS Configuration
```http
Access-Control-Allow-Origin: https://username.github.io
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Sec-WebSocket-Protocol
```

### Input Validation
- All JSON messages validated against schemas
- Question content sanitized for injection attacks
- Context chunk IDs validated against database
- Session IDs validated for format and existence

### Connection Security
- WSS required (secure WebSocket)
- Origin header validation
- Rate limiting by IP address
- Automatic disconnection for abusive behavior

## Performance Requirements

### Latency Targets
- Connection establishment: < 100ms
- First response chunk: < 2000ms (95th percentile)
- Subsequent chunks: < 100ms interval
- Total response time: < 5000ms

### Throughput Targets
- Concurrent connections: 50
- Messages per second: 100
- Questions per minute: 500

## Testing Scenarios

### Happy Path
1. Client connects → receives welcome message
2. Client sends question → receives response_start, multiple response_chunk, response_end
3. Client sends ping → receives pong
4. Client gracefully disconnects

### Error Scenarios
1. Invalid JSON → error message, connection remains open
2. Rate limit exceeded → error with retry_after
3. Backend service down → error with SERVICE_UNAVAILABLE
4. Malicious input → error, potential disconnection

### Edge Cases
1. Empty question → error
2. Very long question → error
3. Invalid context chunks → error
4. Connection timeout → automatic cleanup

## Client Implementation Guidelines

### Connection Management
- Implement automatic reconnection with exponential backoff
- Handle connection errors gracefully
- Maintain session state across reconnections
- Display connection status to user

### Message Handling
- Validate all outgoing messages against schemas
- Handle all message types from server
- Implement timeout for question responses
- Queue messages during disconnection

### Error Handling
- Display user-friendly error messages
- Implement retry logic for retryable errors
- Log errors for debugging
- Provide fallback functionality

### Performance Optimization
- Buffer response chunks for smooth display
- Implement typing indicators
- Preload common responses
- Cache session data locally