# Quickstart Guide: Chatbot Agent Integration

## Overview

This guide provides step-by-step instructions to set up and run the chatbot agent integration with OpenAI Agent SDK and Gemini model.

## Prerequisites

- Python 3.13
- Qdrant vector database running (should already be set up from RAG system)
- Access to Gemini API (Google AI API key)
- Access to OpenRouter API (for Gemini access via OpenAI-compatible interface)

## Environment Setup

1. **Set up environment variables** in your `.env` file:

```bash
# Gemini API access (via OpenRouter)
OPENROUTER_KEY=your_openrouter_api_key
BASE_URL=https://openrouter.ai/api/v1
MODEL=gemini-2.5-flash  # or your preferred Gemini model

# For tracing (optional)
OPENAI_API_KEY=your_openai_api_key  # Only for enabling tracing

# Qdrant configuration (should already be set up)
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=robotics_embeddings
```

2. **Install required dependencies**:

```bash
cd backend
pip install agents python-dotenv
```

Note: The agents library and other dependencies should be added to your requirements.txt file.

## Architecture Overview

The chatbot agent integration extends the existing RAG system with:

1. **Agent Service** (`src/services/agent_service.py`): Core agent logic with retrieval tool
2. **Agent Endpoint** (`src/api/agent_endpoint.py`): API interface for chat interactions
3. **Data Models**: Extended models for session management and agent responses
4. **Integration**: Leverages existing retrieval and Qdrant infrastructure

## Key Components

### 1. Agent Service

The agent service orchestrates the conversation flow:

```python
# Pseudo-code for the agent service
class AgentService:
    def __init__(self):
        self.retrieval_service = RAGIntegrationService()
        self.agent = self._create_agent()

    async def process_message(self, chat_request: ChatRequest) -> ChatResponse:
        # Retrieve relevant content
        retrieved_content = await self.retrieval_service.get_relevant_content_with_context(...)

        # Format content for agent
        context = self._format_context_for_agent(retrieved_content)

        # Generate response with agent
        agent_response = await self._run_agent_with_context(chat_request.message, context)

        # Format and return response
        return self._format_response(agent_response, retrieved_content)
```

### 2. Retrieval Tool

The agent uses a custom tool to retrieve content from Qdrant:

```python
# Pseudo-code for the retrieval tool
async def retrieve_robotics_content(query: str) -> List[RetrievedContent]:
    rag_service = RAGIntegrationService()
    return await rag_service.get_relevant_content_for_query(query)
```

## Running the System

1. **Start Qdrant** (if not already running):
```bash
docker run -p 6333:6333 qdrant/qdrant
```

2. **Verify Qdrant data**:
```bash
python test_qdrant_retrieval.py
```

3. **Start the backend**:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

4. **Test the chat endpoint**:
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is forward kinematics?",
    "session_id": null,
    "require_sources": true
  }'
```

## API Endpoints

### Chat Endpoint
- **URL**: `POST /api/v1/chat`
- **Request**: `ChatRequest`
- **Response**: `ChatResponse`

### Session Management (future extension)
- **URL**: `GET /api/v1/session/{session_id}`
- **URL**: `DELETE /api/v1/session/{session_id}`

## Configuration Options

### Agent Configuration
The agent can be configured with various parameters:

- `temperature`: Controls randomness (0.0-1.0, default 0.7)
- `max_tokens`: Maximum tokens in response (default 1000)
- `top_k`: Number of results to retrieve (default 5)
- `require_sources`: Whether to enforce source citations (default true)

### Performance Tuning
- Adjust `top_k` based on response quality needs
- Tune `min_relevance_score` for content filtering
- Configure caching TTL for retrieved content

## Testing

### Unit Tests
```bash
pytest tests/unit/test_agent_service.py
```

### Integration Tests
```bash
pytest tests/integration/test_agent_endpoint.py
```

### End-to-End Tests
```bash
pytest tests/e2e/test_chatbot_flow.py
```

## Troubleshooting

### Common Issues

1. **API Key Issues**: Verify GEMINI_API_KEY and OPENROUTER_KEY are set correctly
2. **Qdrant Connection**: Ensure Qdrant is running and accessible
3. **Model Availability**: Check that the specified Gemini model is available
4. **Rate Limits**: Monitor for API rate limiting on both retrieval and generation

### Debugging
Enable detailed logging by setting:
```bash
LOG_LEVEL=DEBUG
```

## Next Steps

1. Implement the agent service with the data models defined
2. Create the API endpoints for chat interactions
3. Add proper error handling and fallback responses
4. Implement session management for conversation continuity
5. Add monitoring and analytics for response quality