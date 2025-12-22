# ADR-0001: Backend Architecture and Tech Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-18
- **Feature:** 001-chatbot-agent-integration
- **Context:** The robotics book chatbot agent integration requires a robust backend architecture that integrates with existing systems while supporting AI agent functionality. The decision encompasses the core technology stack, framework choices, and integration approach with the existing codebase.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- **Language**: Python 3.13 (maintains consistency with existing codebase)
- **Web Framework**: FastAPI (for async support, type hints, and OpenAPI documentation)
- **AI Integration**: OpenAI Agent SDK with custom model configuration for Gemini
- **Integration Pattern**: Extend existing backend structure rather than creating standalone service
- **Async Operations**: Leverage async/await for improved performance with AI and database calls
- **Dependency Management**: Use existing requirements.txt approach with minimal new dependencies

## Consequences

### Positive

- Consistent with existing backend architecture and team expertise
- FastAPI provides excellent async support for handling concurrent AI requests
- Type safety through Pydantic models reduces runtime errors
- Automatic API documentation generation
- Minimal operational overhead (no new deployment infrastructure)
- Leverages existing error handling, logging, and monitoring patterns

### Negative

- Tightly coupled to existing codebase, making future refactoring more complex
- Potential performance bottlenecks if AI response times are high
- May require modifications to existing backend components
- Learning curve for team members unfamiliar with Agent SDK patterns

## Alternatives Considered

Alternative Stack A: Standalone microservice in Node.js/TypeScript
- Why rejected: Would introduce new technology stack, increase operational complexity, and create additional deployment and monitoring requirements

Alternative Stack B: Separate Python service with different framework (Flask)
- Why rejected: Would not leverage FastAPI's async capabilities and type safety benefits, and would still require integration work

Alternative Stack C: Serverless functions (AWS Lambda, etc.)
- Why rejected: Cold start times would negatively impact user experience for chatbot interactions, and would complicate session management

## References

- Feature Spec: /specs/001-chatbot-agent-integration/spec.md
- Implementation Plan: /specs/001-chatbot-agent-integration/plan.md
- Related ADRs: ADR-0002 (AI Agent Integration Strategy), ADR-0003 (RAG Integration Approach)
- Evaluator Evidence: /specs/001-chatbot-agent-integration/research.md
