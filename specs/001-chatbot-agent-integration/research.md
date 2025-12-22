# Research: Chatbot Agent Integration

## Summary

This research document covers the investigation into integrating OpenAI Agent SDK with a Gemini model for the robotics book chatbot. It includes analysis of the current system architecture, reference implementations, and technical requirements.

## Current System Architecture

### Backend Structure
- **Main Application**: FastAPI application in `backend/main.py`
- **Retrieval System**: Located in `backend/src/retrieval/` with:
  - API endpoints in `api/retrieval_endpoint.py`
  - Services in `services/retrieval_service.py` and `services/rag_integration_service.py`
  - Models in `models/` directory
  - Configuration in `config.py`
  - Utilities for Qdrant integration, caching, and relevance calculation

### Current RAG Implementation
- Uses Qdrant vector database for semantic search
- Implements context-aware retrieval with conversation history
- Has built-in caching, rate limiting, and relevance filtering
- Supports both single and batch retrieval operations
- Already has a RAG integration service ready for chatbot use

## Reference Implementation Analysis

### OpenAI Agent SDK with Gemini Model
From the reference files in `@References/`:
- `00_simple_agent.py` shows basic agent setup using the `agents` library
- `gemini_model.py` demonstrates how to configure Gemini model with OpenAI client via custom base URL
- Uses AsyncOpenAI client with custom base URL for Gemini API
- Implements basic conversation loop with user input

### Key Components Identified
1. **Agent**: Core component that processes user input with instructions and tools
2. **Runner**: Executes agent runs with specific configurations
3. **RunConfig**: Configuration for model execution with tracing
4. **OpenAIChatCompletionsModel**: Model wrapper for custom models like Gemini

## Technical Integration Strategy

### Approach 1: Direct Integration with Existing RAG
- Use the existing `RAGIntegrationService` to retrieve relevant content
- Create a custom tool for the agent that calls the retrieval service
- Integrate with the existing Qdrant-based retrieval system
- Leverage existing caching, filtering, and context enhancement

### Approach 2: Custom Agent Service
- Create a new agent service that wraps the existing retrieval functionality
- Implement conversation context management
- Add source attribution to responses
- Handle cases where no relevant content is found

## Dependencies and Requirements

### Required Dependencies
- `agents` library (from reference implementation)
- `openai` library for AsyncOpenAI client
- Existing backend dependencies (FastAPI, Qdrant client, etc.)

### Configuration Requirements
- GEMINI_API_KEY in environment variables
- Custom base URL for Gemini API
- Model configuration for Gemini (e.g., gemini-2.5-flash)

## Implementation Considerations

### Conversation Context Management
- Need to maintain conversation history for context-aware responses
- Current system has `QueryContext` with conversation history support
- Should integrate with existing session management approach

### Source Attribution
- Retrieved content already includes source_file and source_location
- Need to format this information appropriately in agent responses
- Must ensure responses are grounded in retrieved content

### Error Handling
- Handle cases where no relevant content is found
- Manage agent unavailability or timeouts
- Graceful fallback responses when retrieval fails

## Open Questions and Clarifications

1. **Model Selection**: Which specific Gemini model should be used? (gemini-2.5-flash, gemini-1.5-pro, etc.)
2. **Tracing**: Should tracing be enabled for production use?
3. **Session Management**: How should conversation context be persisted across requests?
4. **Rate Limiting**: How to handle rate limits for both Qdrant retrieval and Gemini API calls?

## Recommended Architecture

Based on the research, the recommended approach is to:

1. Create a new API endpoint for the chatbot agent in the existing FastAPI application
2. Use the existing RAG integration service to retrieve content
3. Implement an agent tool that calls the retrieval service
4. Create a custom agent service that manages conversation context
5. Ensure proper source attribution in responses

This approach leverages the existing robust retrieval infrastructure while adding the agent capabilities on top.

## Next Steps

1. Design the data models for chatbot sessions and agent responses
2. Define contracts for the agent integration API
3. Implement the agent service with proper error handling
4. Integrate with the existing retrieval system
5. Add proper testing for the agent functionality