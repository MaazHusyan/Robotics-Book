# ADR-0003: Real-time Communication

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-12
- **Feature:** 001-rag-chatbot
- **Context:** The RAG chatbot requires real-time streaming responses to provide an interactive tutoring experience. The constitution mandates streaming answers in real time via WebSocket, with support for text selection context and concurrent user interactions. The system must handle bidirectional communication with <2s response times.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Implement a WebSocket-based real-time communication architecture using FastAPI with connection management and async streaming:

- **Protocol**: Secure WebSocket (WSS) for encrypted communication
- **Backend**: FastAPI WebSocket with async/await patterns
- **Connection Management**: Custom ConnectionManager class for session handling
- **Message Protocol**: Structured JSON messages with type-based routing
- **Streaming**: Real-time response streaming with response_start/response_chunk/response_end pattern
- **Security**: Rate limiting, CORS configuration, input validation
- **Concurrency**: Async connection pooling for multiple simultaneous users
- **Error Handling**: Graceful error propagation and connection recovery

## Consequences

### Positive

- **Real-time Experience**: Streaming responses provide immediate feedback and better user experience
- **Bidirectional Communication**: Supports both questions and context chunk transmission
- **Scalability**: Async architecture handles multiple concurrent connections efficiently
- **Security**: Built-in WebSocket security with additional rate limiting and validation
- **Performance**: Native async support minimizes latency and resource usage
- **Flexibility**: Structured message protocol allows easy extension of functionality
- **Connection Management**: Robust session handling with cleanup and error recovery

### Negative

- **Connection Complexity**: WebSocket connections require careful state management and error handling
- **Scalability Limits**: Single server WebSocket connections have horizontal scaling challenges
- **Browser Compatibility**: Some older browsers may have WebSocket limitations
- **Debugging Difficulty**: Real-time communication is harder to debug than HTTP requests
- **Infrastructure Requirements**: Requires WebSocket-enabled hosting infrastructure
- **Connection Overhead**: Maintaining persistent connections uses server resources
- **Network Sensitivity**: WebSocket connections more sensitive to network issues than HTTP

## Alternatives Considered

**Alternative A: Server-Sent Events (SSE)**
- Unidirectional server-to-client communication over HTTP
- Pros: Simpler implementation, better browser compatibility, auto-reconnection
- Cons: Unidirectional only (no client-to-server), no binary support
- Rejected: Cannot handle text selection context transmission from client to server

**Alternative B: Long Polling**
- Repeated HTTP requests with delayed responses
- Pros: Works through firewalls, compatible with all browsers, simple implementation
- Cons: Higher latency, more server resources, poor user experience
- Rejected: Does not meet constitution requirement for real-time streaming

**Alternative C: Socket.IO**
- WebSocket library with additional features and fallbacks
- Pros: Automatic fallbacks, room management, broadcast capabilities
- Cons: Additional dependency, larger bundle size, not needed for simple use case
- Rejected: Over-engineering for single chatbot use case, adds unnecessary complexity

**Alternative D: gRPC Streaming**
- Bidirectional streaming over HTTP/2
- Pros: Excellent performance, strong typing, efficient binary protocol
- Cons: Limited browser support, requires additional proxy infrastructure
- Rejected: Poor browser compatibility makes it unsuitable for web-based chatbot

**Alternative E: HTTP Chunked Transfer**
- Streaming HTTP responses with chunked encoding
- Pros: Uses standard HTTP infrastructure, simpler than WebSockets
- Cons: No bidirectional communication, connection per request overhead
- Rejected: Cannot handle the interactive nature of chat with context chunks

## References

- Feature Spec: specs/001-rag-chatbot/spec.md
- Implementation Plan: specs/001-rag-chatbot/plan.md
- Research Findings: specs/001-rag-chatbot/research.md
- WebSocket API Contract: specs/001-rag-chatbot/contracts/websocket-api.md
- Constitution: .specify/memory/constitution.md
- Related ADRs: ADR-0001 (AI Integration Stack), ADR-0002 (Vector Database Architecture)
