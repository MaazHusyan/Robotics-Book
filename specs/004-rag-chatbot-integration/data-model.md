# Data Model: RAG Chatbot Integration (Updated)

## Entities

### User Query
- **Fields**:
  - `text`: str - The user's query text
  - `session_id`: Optional[str] - Identifier for conversation session
  - `context`: QueryContext - Additional context for the query
- **Relationships**: Connected to conversation session
- **Validation**: Must be non-empty, max 10,000 characters
- **State transitions**: N/A

### QueryContext
- **Fields**:
  - `conversation_history`: List[dict] - Previous conversation turns
  - `selected_text`: Optional[str] - Text selected by user for focus
  - `filters`: Dict[str, Any] - Additional filters for retrieval
- **Relationships**: Associated with User Query
- **Validation**: Conversation history items must have 'role' and 'content'
- **State transitions**: N/A

### RetrievedContent
- **Fields**:
  - `id`: str - Unique identifier for the content chunk
  - `chunk_id`: str - Identifier for the specific chunk
  - `content`: str - The actual content text
  - `source_file`: str - Name of the source file
  - `source_location`: str - Location within the source (e.g., chapter, page)
  - `relevance_score`: float - Score indicating relevance to query (0.0-1.0)
  - `metadata`: Dict[str, Any] - Additional metadata about the content
  - `embedding_vector`: Optional[List[float]] - Vector representation of content
- **Relationships**: Result of content retrieval based on User Query
- **Validation**: Content, source_file, and source_location must be non-empty
- **State transitions**: N/A

### ChatSession
- **Fields**:
  - `session_id`: str - Unique identifier for the session
  - `user_id`: Optional[str] - Identifier for the user (if authenticated)
  - `created_at`: datetime - Timestamp when session was created
  - `updated_at`: datetime - Timestamp when session was last updated
  - `conversation_history`: List[dict] - History of conversation turns
- **Relationships**: Contains multiple conversation turns (User Query and Agent Response pairs)
- **Validation**: session_id must be unique, conversation_history items must have role and content
- **State transitions**: N/A

### AgentQuery
- **Fields**:
  - `query_text`: str - The original query text
  - `session_id`: str - Session identifier
  - `require_sources`: bool - Whether to require source citations
  - `max_tokens`: Optional[int] - Maximum tokens for response
  - `temperature`: Optional[float] - Temperature for response generation (0.0-1.0)
  - `conversation_context`: Dict - Context from conversation history and retrieved content
- **Relationships**: Associated with ChatSession and contains RetrievedContent
- **Validation**: Query text must be non-empty, temperature must be between 0.0-1.0
- **State transitions**: N/A

### AgentResponse
- **Fields**:
  - `session_id`: str - Session identifier
  - `query`: str - Original query text
  - `response`: str - Generated response text
  - `sources`: List[dict] - Retrieved content used in response
  - `conversation_turn`: int - Turn number in the conversation
  - `timestamp`: datetime - When response was generated
  - `response_time`: float - Time taken to generate response
  - `has_relevant_content`: bool - Whether relevant content was found
  - `tokens_used`: Optional[int] - Number of tokens used in response
  - `error`: Optional[str] - Error message if any occurred
- **Relationships**: Response to AgentQuery within ChatSession
- **Validation**: Response must be non-empty when no errors occurred
- **State transitions**: N/A

### AgentConfig
- **Fields**:
  - `model_name`: str - Name of the LLM model to use
  - `temperature`: float - Default temperature for responses (0.0-1.0)
  - `max_tokens`: int - Default maximum tokens for responses
  - `top_k`: int - Number of top results to retrieve
  - `min_relevance_score`: float - Minimum relevance score threshold
  - `enable_tracing`: bool - Whether to enable tracing
  - `timeout_seconds`: int - Timeout for API calls
  - `fallback_response`: str - Response to use if processing fails
- **Relationships**: Configuration for AgentService
- **Validation**: Temperature between 0.0-1.0, max_tokens and top_k positive, timeout positive
- **State transitions**: N/A

### AgentToolResult (from reference files)
- **Fields**:
  - `tool_name`: str - Name of the tool that was executed
  - `success`: bool - Whether the tool execution was successful
  - `content`: List[dict] - Content returned by the tool
  - `error`: Optional[str] - Error message if tool failed
  - `execution_time`: float - Time taken to execute the tool
- **Relationships**: Result of tool execution within the agent framework
- **Validation**: Must have either success=true with content or success=false with error
- **State transitions**: N/A