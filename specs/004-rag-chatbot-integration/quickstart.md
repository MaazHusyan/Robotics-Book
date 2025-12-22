# Quickstart: RAG Chatbot Integration (Updated)

## Prerequisites

- Python 3.13
- Qdrant vector database running (local or remote)
- OpenRouter API key for LLM access (or alternative LLM provider)
- Environment variables configured (see `.env.example`)
- Agents framework installed (from reference files)

## Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   pip install agents  # Required for the agent framework from reference files
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration:
   # OPENROUTER_KEY=your_openrouter_key
   # QDRANT_HOST=localhost
   # QDRANT_PORT=6333
   # MODEL=your_model_name
   ```

3. **Start Qdrant** (if using locally):
   ```bash
   # Using Docker
   docker run -p 6333:6333 -p 6334:6334 \
     -v $(pwd)/qdrant_storage:/qdrant/storage:z \
     qdrant/qdrant
   ```

4. **Run the backend server**:
   ```bash
   cd backend
   python main.py
   ```

## Usage

### API Endpoints

1. **Chat Endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What is humanoid robotics?",
       "session_id": "optional-session-id",
       "require_sources": true,
       "temperature": 0.7
     }'
   ```

2. **Get Session**:
   ```bash
   curl http://localhost:8000/api/v1/session/{session_id}
   ```

3. **Clear Session**:
   ```bash
   curl -X DELETE http://localhost:8000/api/v1/session/{session_id}
   ```

### Python Client Example

```python
import httpx
import json

async def chat_with_robotics_bot():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/chat",
            json={
                "message": "Explain the basics of robotic kinematics",
                "require_sources": True
            },
            headers={"Content-Type": "application/json"}
        )
        return response.json()

# Example usage
import asyncio
result = asyncio.run(chat_with_robotics_bot())
print(result)
```

## Reference File Integration

The implementation adapts the following reference files:

1. **rag_agent.py**: The core agent logic is adapted from this file, including:
   - Agent creation with `agents.Agent`
   - Tool definition with `@function_tool` decorator
   - `get_embedding` function with fallback mechanism
   - Agent instructions preventing hallucination

2. **qdrant_retrieve.py**: Qdrant retrieval patterns are adapted from this file, including:
   - Connection handling for different Qdrant configurations
   - Query point operations for similarity search
   - Error handling and result processing

3. **gemini_model.py**: Model configuration is adapted from this file, including:
   - AsyncOpenAI client setup
   - Model configuration using OpenRouter
   - RunConfig for agent execution

## Configuration

Key environment variables:
- `OPENROUTER_KEY`: API key for OpenRouter access
- `MODEL`: Model name to use (e.g., "gemini/gemini-2.5-flash")
- `QDRANT_HOST`: Host for Qdrant database
- `QDRANT_PORT`: Port for Qdrant database
- `QDRANT_API_KEY`: API key for Qdrant (if required)
- `BOOK_NAME`: Name of the book for the chatbot

## Testing

Run the tests to verify functionality:
```bash
cd backend
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
```