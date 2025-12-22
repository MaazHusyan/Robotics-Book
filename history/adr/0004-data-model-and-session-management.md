# ADR-0004: Data Model and Session Management

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-18
- **Feature:** 001-chatbot-agent-integration
- **Context:** The chatbot requires proper data modeling for conversations, session management to maintain context across requests, and source attribution for retrieved content. This decision covers the data structures, session persistence strategy, and conversation management approach.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- **Data Models**: Use Pydantic models for type safety and validation (ChatSession, AgentQuery, AgentResponse, RetrievedContent)
- **Session Management**: UUID-based session identifiers with in-memory/Redis storage for conversation context
- **Conversation History**: Store conversation turns as structured data with role, content, and timestamp
- **Source Attribution**: Preserve existing RetrievedContent model with source_file and source_location metadata
- **Session Persistence**: Short-term in memory/Redis, long-term in database if needed
- **API Models**: Separate request/response models (ChatRequest, ChatResponse) for API layer
- **Agent Configuration**: Centralized AgentConfig model for model parameters and behavior settings

## Consequences

### Positive

- Strong type safety reduces runtime errors and improves developer experience
- Consistent data structure across the application
- Proper session management enables contextual conversations
- Maintains source attribution for responsible AI responses
- Clear separation between internal models and API contracts
- Extensible design for future features and analytics

### Negative

- Memory overhead for maintaining conversation history
- Complexity of session state management across deployments
- Potential privacy concerns with conversation data retention
- Additional database queries if sessions are persisted long-term
- Risk of session data growing too large over extended conversations

## Alternatives Considered

Alternative Stack A: No session management, stateless conversations
- Why rejected: Would lose conversation context which is essential for natural chatbot interactions

Alternative Stack B: Client-side session management
- Why rejected: Would expose conversation history to client, security concerns, and wouldn't work across devices

Alternative Stack C: External session store (separate database service)
- Why rejected: Would add operational complexity and additional network calls, impacting performance

## References

- Feature Spec: /specs/001-chatbot-agent-integration/spec.md
- Implementation Plan: /specs/001-chatbot-agent-integration/plan.md
- Related ADRs: ADR-0001 (Backend Architecture and Tech Stack), ADR-0003 (RAG Integration Approach)
- Evaluator Evidence: /specs/001-chatbot-agent-integration/data-model.md, /specs/001-chatbot-agent-integration/research.md
