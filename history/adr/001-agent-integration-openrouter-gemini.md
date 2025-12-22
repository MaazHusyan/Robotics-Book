# ADR: Agent Integration with OpenAI SDK and Gemini via OpenRouter

## Status
Accepted

## Context
We needed to implement a chatbot agent that could interact with users about robotics topics, using the existing RAG (Retrieval Augmented Generation) infrastructure. The agent needed to be able to retrieve relevant content from the robotics book collection in Qdrant and generate contextually relevant responses with proper source citations.

## Decision
We decided to use the OpenAI Agent SDK with the Google Gemini model accessed through OpenRouter. This approach allows us to:

1. Leverage the existing OpenAI-compatible interface to access Gemini models
2. Use the agents library to create a conversational agent
3. Integrate with our existing RAG infrastructure by creating custom tools
4. Maintain conversation context and session management

## Alternatives Considered
1. Direct integration with Google's Gemini API - would require different SDK and potentially more custom code
2. Using OpenAI's GPT models - would require different API keys and potentially different pricing model
3. Building a custom agent from scratch - would require significant additional development time
4. Using other LLM providers like Anthropic - would require different integration patterns

## Consequences
### Positive
- Can leverage existing OpenAI SDK knowledge and patterns
- Access to Gemini's specific capabilities for technical content
- Maintains consistency with existing RAG infrastructure
- Allows for custom tools to access our specific knowledge base

### Negative
- Adds dependency on OpenRouter service
- Potential latency from routing through OpenRouter
- Possible cost implications of using external service
- Requires managing additional API keys

## Links
- Implementation: backend/src/services/agent_service.py
- API: backend/src/api/agent_endpoint.py