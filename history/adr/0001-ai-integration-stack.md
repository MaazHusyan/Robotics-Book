# ADR-0001: AI Integration Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-12
- **Feature:** 001-rag-chatbot
- **Context:** The RAG chatbot requires AI integration for question answering, text embedding generation, and agent orchestration. The constitution mandates use of OpenAI Agents SDK with Gemini via OpenAI-compatible endpoint, requiring careful integration of multiple AI services while maintaining educational value and source citation requirements.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Adopt an integrated AI stack combining Gemini models via OpenAI-compatible endpoint with OpenAI Agents SDK for orchestration:

- **LLM Integration**: Gemini 1.5 Flash via OpenAI-compatible endpoint (generativelanguage.googleapis.com/v1beta/openai/)
- **Embedding Model**: Gemini text-embedding-004 with 768-dimensional vectors
- **Agent Framework**: OpenAI Agents SDK for tool orchestration and response streaming
- **Task Type**: RETRIEVAL_DOCUMENT for optimized content indexing
- **System Prompt**: Robotics Book Tutor persona with explicit citation requirements and source constraints

## Consequences

### Positive

- **Unified Integration**: Single API interface through OpenAI SDK while leveraging Gemini's capabilities
- **Streaming Support**: Native streaming responses for real-time chat experience
- **Tool Orchestration**: Built-in tool calling for content retrieval and context management
- **Cost Efficiency**: Gemini pricing typically more favorable than OpenAI for equivalent capabilities
- **Educational Focus**: Ability to craft specific system prompts for tutoring behavior
- **Constitution Compliance**: Meets requirement for OpenAI Agents SDK + Gemini combination

### Negative

- **API Compatibility Risks**: Reliance on OpenAI-compatible endpoint which may have subtle differences
- **Single Vendor Lock-in**: Committed to Gemini ecosystem for embeddings and generation
- **Limited Model Options**: Cannot easily switch to other providers without code changes
- **Debugging Complexity**: Additional abstraction layer makes error tracing more difficult
- **Rate Limiting**: Subject to both Gemini API limits and OpenAI SDK constraints

## Alternatives Considered

**Alternative A: Direct Gemini API Integration**
- Use Google's generative-ai SDK directly
- Pros: Native support, all Gemini features available
- Cons: Would require custom agent implementation, no streaming support
- Rejected: Lacked built-in agent orchestration and streaming capabilities

**Alternative B: OpenAI GPT Stack**
- OpenAI GPT-4 + OpenAI embeddings + OpenAI Assistants API
- Pros: Native SDK support, mature ecosystem
- Cons: Higher costs, violates constitution requirement for Gemini
- Rejected: Constitution explicitly requires Gemini integration

**Alternative C: LangChain Integration**
- LangChain with Gemini provider + custom agent chain
- Pros: Rich framework features, multiple provider support
- Cons: Additional complexity, performance overhead, larger dependency footprint
- Rejected: Over-engineering for single-purpose chatbot, adds unnecessary abstraction

**Alternative D: Anthropic Claude Integration**
- Claude 3.5 Sonnet via custom implementation
- Pros: Strong reasoning capabilities
- Cons: No OpenAI-compatible endpoint, requires custom streaming implementation
- Rejected: Would require significant custom development for streaming and tool use

## References

- Feature Spec: specs/001-rag-chatbot/spec.md
- Implementation Plan: specs/001-rag-chatbot/plan.md
- Research Findings: specs/001-rag-chatbot/research.md
- Data Model: specs/001-rag-chatbot/data-model.md
- Constitution: .specify/memory/constitution.md
- Related ADRs: ADR-0002 (Vector Database Architecture), ADR-0003 (Real-time Communication)
