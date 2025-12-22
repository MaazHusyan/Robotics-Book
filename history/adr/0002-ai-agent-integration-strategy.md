# ADR-0002: AI Agent Integration Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-18
- **Feature:** 001-chatbot-agent-integration
- **Context:** The system needs to integrate AI agent capabilities for conversational robotics book content retrieval. This decision covers the approach for using the OpenAI Agent SDK with a Gemini model, configuration, and execution patterns.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- **Agent SDK**: Use OpenAI Agent SDK for agent orchestration and execution management
- **Model Configuration**: Configure AsyncOpenAI client with custom base URL to access Gemini model
- **Agent Runner**: Implement using Runner pattern for executing agent runs with configuration
- **Model Wrapper**: Use OpenAIChatCompletionsModel wrapper for custom model integration
- **Run Configuration**: Implement RunConfig for model execution with optional tracing
- **API Access**: Use GEMINI_API_KEY environment variable for authentication

## Consequences

### Positive

- Leverages mature Agent SDK for complex conversation flows
- Flexible model configuration allows for different AI providers
- Built-in tracing capabilities for debugging and monitoring
- Consistent API pattern with existing OpenAI integrations
- Extensible architecture for adding additional tools and functions

### Negative

- Vendor lock-in to OpenAI Agent SDK patterns and future changes
- Complexity of agent orchestration may impact performance
- Dependency on external AI service availability and rate limits
- Potential cost implications from AI service usage
- Learning curve for team members with agent patterns

## Alternatives Considered

Alternative Stack A: Direct Gemini API calls without Agent SDK
- Why rejected: Would lose agent orchestration benefits, tool calling capabilities, and conversation management features

Alternative Stack B: OpenAI GPT models instead of Gemini
- Why rejected: Project specifically requires Gemini model for performance/cost reasons or existing agreements

Alternative Stack C: Open-source models (e.g., Ollama, Hugging Face)
- Why rejected: Would require significant infrastructure setup, model hosting, and maintenance overhead

## References

- Feature Spec: /specs/001-chatbot-agent-integration/spec.md
- Implementation Plan: /specs/001-chatbot-agent-integration/plan.md
- Related ADRs: ADR-0001 (Backend Architecture and Tech Stack), ADR-0003 (RAG Integration Approach)
- Evaluator Evidence: /specs/001-chatbot-agent-integration/research.md
