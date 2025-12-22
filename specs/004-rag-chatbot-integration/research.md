# Research: RAG Chatbot Integration (Updated)

## Decision: Technology Stack Selection
**Rationale**: Based on the existing codebase and reference files, the RAG chatbot will use:
- Python 3.13 with FastAPI for the backend API
- Qdrant vector database for semantic search (using patterns from `@References/qdrant_retrieve.py`)
- Agent pattern from `@References/rag_agent.py` with `agents.Agent`, `Runner`, and `function_tool`
- Model configuration from `@References/gemini_model.py` using OpenRouter/Gemini API
- The existing backend structure in `/backend/src/`

## Decision: Architecture Pattern
**Rationale**: Adapt the existing agent implementation from `@References/rag_agent.py` rather than creating new services from scratch. The implementation will:
- Use the agent pattern with `agents.Agent`, `Runner`, and `function_tool` from rag_agent.py
- Use the `retrieve_book_data` function and `get_embedding` function from rag_agent.py
- Use the Qdrant connection patterns from qdrant_retrieve.py
- Use the model configuration from gemini_model.py using OpenRouter/Gemini
- Maintain the conversation session management using SQLiteSession

## Alternatives Considered:

1. **Alternative LLM providers**: OpenAI vs Gemini vs OpenRouter
   - Chosen: OpenRouter with configurable model to allow flexibility (as in reference files)

2. **Alternative vector databases**: Qdrant vs Pinecone vs Weaviate vs Chroma
   - Chosen: Qdrant as it's already in the reference files and codebase

3. **Alternative embedding models**: Sentence Transformers vs Jina AI vs Cohere vs OpenAI
   - Chosen: Using the embedding approach from reference files with fallback to hash-based embedding

4. **Architecture approaches**: Standalone script vs Integrated service vs Microservice
   - Chosen: Adapt existing agent implementation from reference files and wrap in FastAPI endpoints

## Reference File Integration Points:

1. `@References/rag_agent.py` - Contains complete RAG agent implementation with:
   - Agent pattern using `agents.Agent`, `Runner`, and `function_tool`
   - `retrieve_book_data` function as a tool for the agent
   - `get_embedding` function for text embedding with fallback
   - Conversation session management using SQLiteSession
   - Agent instructions that prevent hallucination

2. `@References/qdrant_retrieve.py` - Contains:
   - Qdrant connection patterns with multiple configuration options (cloud, authenticated, local)
   - `retrieve_data_from_qdrant_collection` function with proper error handling
   - Query point and scroll operations for similarity search

3. `@References/gemini_model.py` - Contains:
   - Model configuration using OpenRouter API
   - AsyncOpenAI client setup
   - RunConfig for the agent execution

## Integration Strategy:
- Adapt the agent implementation from rag_agent.py to work within the existing backend structure
- Use the Qdrant retrieval patterns from qdrant_retrieve.py for consistency
- Integrate the model configuration from gemini_model.py
- Wrap the agent functionality in FastAPI endpoints for web access
- Maintain compatibility with existing embedding services (Jina AI, Cohere) where possible