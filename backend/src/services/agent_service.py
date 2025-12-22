"""
Agent service implementation for the chatbot agent integration.

Based on the service-contract.md specification for the 001-chatbot-agent-integration feature.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import asyncio
import logging
import os
from dotenv import load_dotenv

from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, RunConfig

from ..models.query_models import Query
from ..models.content_models import RetrievedContent
from ..models.agent_models import (
    ChatSession, AgentQuery, AgentResponse, AgentConfig,
    ChatRequest, ChatResponse, AgentToolResult
)
from .rag_integration_service import RAGIntegrationService
from agents import function_tool


logger = logging.getLogger(__name__)


class AgentServiceInterface(ABC):
    """
    Abstract interface for the agent service
    """

    @abstractmethod
    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        require_sources: bool = True,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AgentResponse:
        """
        Process a user message through the agent and return a response.

        Args:
            message: The user's message to process
            session_id: Session identifier to maintain conversation context
                       If None, a new session is created
            require_sources: Whether to require source citations in response
            temperature: Controls randomness in agent response (0.0-1.0)
            max_tokens: Maximum number of tokens in the response

        Returns:
            AgentResponse containing the agent's response with sources and metadata

        Raises:
            ValueError: If message is invalid or too short
            RetrievalError: If content retrieval fails
            AgentError: If agent processing fails
        """
        pass

    @abstractmethod
    async def create_session(self, user_id: Optional[str] = None) -> ChatSession:
        """
        Create a new chat session.

        Args:
            user_id: Optional user identifier to associate with the session

        Returns:
            ChatSession with a new session_id and initial state
        """
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Retrieve an existing chat session.

        Args:
            session_id: The session identifier to retrieve

        Returns:
            ChatSession if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_session(self, session: ChatSession) -> bool:
        """
        Update an existing chat session.

        Args:
            session: The ChatSession object to update

        Returns:
            True if update was successful, False otherwise
        """
        pass

    @abstractmethod
    async def clear_session(self, session_id: str) -> bool:
        """
        Clear/terminate a chat session.

        Args:
            session_id: The session identifier to clear

        Returns:
            True if session was cleared, False if session didn't exist
        """
        pass


class AgentService(AgentServiceInterface):
    """
    Concrete implementation of the agent service
    """

    def __init__(self, config: AgentConfig, rag_service: RAGIntegrationService):
        """
        Initialize the agent service.

        Args:
            config: Configuration for agent behavior
            rag_service: Service for content retrieval
        """
        self.config = config
        self.rag_service = rag_service
        self.sessions = {}  # In-memory session storage (use Redis/database in production)

        # Load environment variables
        load_dotenv()

        # Initialize the agent
        self.agent = self._initialize_agent()

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        require_sources: bool = True,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AgentResponse:
        """
        Implementation of process_message with the following contract:

        PRECONDITIONS:
        - message must be a non-empty string with minimum length of 1 character
        - session_id, if provided, must be a valid string identifier
        - temperature, if provided, must be between 0.0 and 1.0
        - max_tokens, if provided, must be a positive integer

        POSTCONDITIONS:
        - Returns an AgentResponse with populated fields
        - If session_id was None, creates a new session and returns new session_id
        - If session_id was provided, updates existing session with new conversation turn
        - Response includes sources if require_sources is True and content is available
        - Response time is logged in the AgentResponse
        - Conversation history is updated in the session

        SIDE EFFECTS:
        - Updates session state in storage
        - May create new session if session_id was None
        - Logs the interaction for monitoring/analysis
        """
        # Input validation and logging
        logger.info(f"Processing message for session {session_id or 'new session'}")
        if not message or len(message.strip()) < 1:
            logger.warning(f"Invalid message received: '{message[:50]}...' (length: {len(message)})")
            raise ValueError("Message must be a non-empty string with at least 1 character")

        if len(message) > 10000:
            logger.warning(f"Message exceeds maximum length: {len(message)} characters")
            raise ValueError("Message exceeds maximum length of 10,000 characters")

        if temperature is not None and (temperature < 0.0 or temperature > 1.0):
            logger.warning(f"Invalid temperature value: {temperature}")
            raise ValueError("Temperature must be between 0.0 and 1.0")

        if max_tokens is not None and max_tokens <= 0:
            logger.warning(f"Invalid max_tokens value: {max_tokens}")
            raise ValueError("Max tokens must be a positive integer")

        # Use provided parameters or fall back to config defaults
        effective_temperature = temperature if temperature is not None else self.config.temperature
        effective_max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens
        effective_require_sources = require_sources

        logger.info(f"Processing message with params - temp: {effective_temperature}, max_tokens: {effective_max_tokens}, sources: {effective_require_sources}")

        start_time = datetime.now()

        # Load or create session
        session = None
        if session_id:
            logger.debug(f"Loading existing session: {session_id}")
            session = await self.get_session(session_id)
            if not session:
                logger.info(f"Session {session_id} not found, creating new session with provided ID")
                # If session doesn't exist, create a new one but use the provided session_id
                session = ChatSession(
                    session_id=session_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                await self.update_session(session)
        else:
            logger.debug("Creating new session for message")
            session = await self.create_session()

        if not session:
            logger.error("Failed to create or retrieve session")
            raise ValueError("Failed to create or retrieve session")

        logger.info(f"Session {session.session_id} loaded, processing message with {len(session.conversation_history)} previous exchanges")

        # Retrieve relevant content using RAG service
        retrieved_content = []
        retrieval_error = None
        if effective_require_sources:
            logger.debug(f"Starting content retrieval for query: '{message[:50]}...'")
            try:
                # Prepare query context with conversation history
                query_context = None
                if session.conversation_history:
                    # Include recent conversation history in the query context
                    recent_history = session.conversation_history[-3:]  # Last 3 exchanges
                    query_context = {"conversation_history": recent_history}
                    logger.debug(f"Using conversation context with {len(recent_history)} previous exchanges")

                # Perform retrieval with context
                retrieved_content = await self.rag_service.get_relevant_content_for_query(
                    query_text=message,
                    top_k=self.config.top_k,
                    session_id=session.session_id if session else None
                )
                logger.info(f"Retrieved {len(retrieved_content)} relevant content items")
            except Exception as e:
                retrieval_error = str(e)
                logger.error(f"Error retrieving content: {retrieval_error}", exc_info=True)
                # Continue without content - the agent will handle this case with fallback

        # Create agent query with context
        logger.debug(f"Creating agent query with {len(retrieved_content) if retrieved_content else 0} content items")
        agent_query = AgentQuery(
            query_text=message,
            session_id=session.session_id,
            require_sources=effective_require_sources,
            max_tokens=effective_max_tokens,
            temperature=effective_temperature,
            conversation_context={"retrieved_content": [content.dict() for content in retrieved_content] if retrieved_content else []}
        )

        # Generate response using the agent
        response_text = ""
        agent_error = None
        logger.debug("Starting agent response generation")
        try:
            response_text = await self._generate_agent_response(agent_query, retrieved_content)
            logger.info(f"Agent response generated successfully, length: {len(response_text)} characters")
        except Exception as e:
            agent_error = str(e)
            logger.error(f"Error generating agent response: {agent_error}", exc_info=True)
            # Use fallback response
            response_text = self.config.fallback_response
            logger.info("Using fallback response due to agent error")

        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Total processing time: {response_time:.2f}s")

        # Additional performance metrics
        content_count = len(retrieved_content) if retrieved_content else 0
        response_length = len(response_text)
        logger.info(f"Performance metrics - Response time: {response_time:.2f}s, Content items: {content_count}, Response length: {response_length} chars")

        # Performance alert if response time exceeds threshold
        if response_time > 5.0:  # 5 second threshold
            logger.warning(f"Performance alert: Response time {response_time:.2f}s exceeded 5s threshold")
        elif response_time > 2.0:
            logger.info(f"Response time {response_time:.2f}s approaching 2s target")

        # Update conversation history in session
        logger.debug(f"Updating session {session.session_id} with new conversation turn")
        session.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now()
        })
        session.conversation_history.append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now(),
            "sources": [content.dict() for content in retrieved_content] if retrieved_content else [],
            "retrieval_error": retrieval_error,
            "agent_error": agent_error
        })
        session.updated_at = datetime.now()

        await self.update_session(session)
        logger.debug(f"Session {session.session_id} updated successfully")

        # Calculate conversation turn number
        conversation_turn = len([entry for entry in session.conversation_history if entry["role"] == "assistant"])

        # Create and return AgentResponse
        agent_response = AgentResponse(
            session_id=session.session_id,
            query=message,
            response=response_text,
            sources=[content.dict() for content in retrieved_content] if retrieved_content else [],
            conversation_turn=conversation_turn,
            timestamp=datetime.now(),
            response_time=response_time,
            has_relevant_content=len(retrieved_content) > 0,
            tokens_used=None  # Will be calculated by the agent if available
        )

        # Add error information if there were any
        if retrieval_error or agent_error:
            error_messages = []
            if retrieval_error:
                error_messages.append(f"Retrieval error: {retrieval_error}")
            if agent_error:
                error_messages.append(f"Agent error: {agent_error}")
            agent_response.error = "; ".join(error_messages)

        logger.info(f"Message processing completed successfully for session {session.session_id}, response length: {len(response_text)}, sources: {len(retrieved_content)}")
        if agent_response.error:
            logger.warning(f"Response contains errors: {agent_response.error}")

        return agent_response

    async def create_session(self, user_id: Optional[str] = None) -> ChatSession:
        """
        Implementation contract:

        PRECONDITIONS:
        - user_id, if provided, must be a valid string

        POSTCONDITIONS:
        - Returns a new ChatSession with unique session_id
        - Session is stored in session storage
        - created_at and updated_at are set to current time
        - conversation_history is initialized as empty list
        """
        session = ChatSession(
            session_id=str(uuid.uuid4()),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            user_id=user_id
        )

        self.sessions[session.session_id] = session
        return session

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Implementation contract:

        PRECONDITIONS:
        - session_id must be a valid string identifier

        POSTCONDITIONS:
        - Returns ChatSession if found in storage, None otherwise
        - Does not modify the session state
        """
        if not session_id:
            return None
        return self.sessions.get(session_id)

    async def update_session(self, session: ChatSession) -> bool:
        """
        Implementation contract:

        PRECONDITIONS:
        - session must be a valid ChatSession object with session_id
        - session.session_id must exist in storage

        POSTCONDITIONS:
        - Updates the session in storage with new values
        - Updates updated_at timestamp
        - Returns True if update was successful, False otherwise
        """
        if not session or not session.session_id:
            return False

        session.updated_at = datetime.now()
        self.sessions[session.session_id] = session
        return True

    async def clear_session(self, session_id: str) -> bool:
        """
        Implementation contract:

        PRECONDITIONS:
        - session_id must be a valid string identifier

        POSTCONDITIONS:
        - Removes session from storage
        - Returns True if session was found and removed, False otherwise
        """
        if not session_id or session_id not in self.sessions:
            return False

        del self.sessions[session_id]
        return True

    async def _generate_agent_response(self, agent_query: AgentQuery, retrieved_content: List[RetrievedContent]) -> str:
        """
        Generate response using the agent with retrieved content.
        """
        if self.agent is None:
            # Fallback if agent is not properly initialized
            if retrieved_content:
                content_snippets = "\n".join([f"- {content.content[:200]}..." for content in retrieved_content[:3]])
                response = f"Based on the robotics book content I found:\n\n{content_snippets}\n\n{agent_query.query_text}"
            else:
                response = self.config.fallback_response
            return response

        # Prepare context from retrieved content with proper source formatting
        context_str = ""
        if retrieved_content:
            logger.info(f"Providing {len(retrieved_content)} content items to agent for query: '{agent_query.query_text[:50]}...'")
            context_str = "Here is relevant information from robotics books to help answer the user's question:\n\n"
            for i, content in enumerate(retrieved_content[:5]):  # Use top 5 results
                context_str += f"Source {i+1}: {content.source_file} - {content.source_location}\n"
                context_str += f"Content: {content.content}\n\n"
        else:
            logger.info(f"No relevant content found for query: '{agent_query.query_text}', using fallback response")
            context_str = "No specific information was found in the robotics books to answer this question. Please try rephrasing your question or ask about a different topic related to robotics. If you're asking about a very specific or advanced topic, it may not be covered in the available content."

        # Create a prompt that includes the context and user query, with instructions for proper source citation
        full_prompt = f"{context_str}\n\nUser Question: {agent_query.query_text}\n\nPlease provide a helpful answer based on the provided context, citing sources when possible. When referencing specific information from the provided content, please clearly indicate which source it comes from (e.g., 'According to Source 1...', or 'Based on the content from robotics_book_chapter_X.pdf...')."

        try:
            # Import SQLiteSession for conversation history
            from .session_manager import session_manager

            # Get or create SQLiteSession for conversation history
            sqlite_session = session_manager.get_session(agent_query.session_id)

            # Run the agent with the prepared prompt and SQLite session for conversation history
            run_result = await Runner.run(
                self.agent,
                full_prompt,
                run_config=RunConfig(
                    model=self.agent.model,
                    model_provider=self.client,
                    tracing_disabled=not self.config.enable_tracing
                ),
                max_turns=3,  # Allow multiple turns for complex queries
                session=sqlite_session  # Add SQLite session for conversation history
            )

            return run_result.final_output if run_result.final_output else self.config.fallback_response
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            # Fallback to simple response if agent fails
            if retrieved_content:
                content_snippets = "\n".join([
                    f"Source {i+1}: {content.source_file} - {content.source_location}\nContent: {content.content[:200]}..."
                    for i, content in enumerate(retrieved_content[:3])
                ])
                response = f"Based on the robotics book content I found:\n\n{content_snippets}\n\n{agent_query.query_text}"
            else:
                response = self.config.fallback_response
            return response

    async def retrieve_robotics_content(self, query: str) -> AgentToolResult:
        """
        Retrieve relevant robotics content using the RAG service.
        This serves as a tool for the agent to access robotics book content.

        Args:
            query: The query to search for in the robotics content

        Returns:
            AgentToolResult containing the retrieved content or error information
        """
        start_time = datetime.now()
        try:
            # Perform retrieval using the RAG service
            retrieved_content = await self.rag_service.get_relevant_content_for_query(
                query=query,
                top_k=self.config.top_k,
                min_relevance_score=self.config.min_relevance_score
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            return AgentToolResult(
                tool_name="retrieve_robotics_content",
                success=True,
                content=[content.dict() for content in retrieved_content],
                execution_time=execution_time
            )
        except Exception as e:
            logger.error(f"Error in retrieve_robotics_content tool: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return AgentToolResult(
                tool_name="retrieve_robotics_content",
                success=False,
                content=[],
                error=str(e),
                execution_time=execution_time
            )

    @function_tool
    async def retrieve_robotics_content_tool(self, query: str) -> str:
        """
        Retrieve relevant robotics content from the robotics book database.

        Args:
            query: The query to search for in the robotics content

        Returns:
            A JSON string containing the retrieved content with sources and relevance scores
        """
        try:
            # Perform retrieval using the RAG service
            retrieved_content = await self.rag_service.get_relevant_content_for_query(
                query_text=query,
                top_k=self.config.top_k,
                min_relevance_score=self.config.min_relevance_score
            )

            # Format the results as a structured response
            if retrieved_content:
                results = []
                for content in retrieved_content:
                    results.append({
                        "id": content.id,
                        "content": content.content,
                        "source_file": content.source_file,
                        "source_location": content.source_location,
                        "relevance_score": content.relevance_score
                    })

                return f"Found {len(results)} relevant sources:\n" + "\n".join([
                    f"Source {i+1}: {item['source_file']} - {item['source_location']}\n"
                    f"Content: {item['content'][:200]}...\n"
                    f"Relevance: {item['relevance_score']:.2f}\n"
                    for i, item in enumerate(results)
                ])
            else:
                return "No relevant content found in the robotics books for the given query."
        except Exception as e:
            logger.error(f"Error in retrieve_robotics_content_tool: {str(e)}")
            return f"Error retrieving content: {str(e)}"

    def _initialize_agent(self):
        """
        Initialize the agent with the appropriate model and configuration.
        """
        # Get environment variables for Gemini API access
        openrouter_api = os.getenv("OPENROUTER_KEY")
        openrouter_base_url = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
        openrouter_model = os.getenv("MODEL", self.config.model_name)

        if not openrouter_api:
            logger.warning("OPENROUTER_KEY not found in environment. Agent functionality will be limited.")
            return None

        # Set up the OpenAI client with OpenRouter API key and base URL
        client = AsyncOpenAI(
            api_key=openrouter_api,
            base_url=openrouter_base_url,
        )

        # Create the model configuration
        model = OpenAIChatCompletionsModel(
            openai_client=client,
            model=openrouter_model
        )

        # Configure the model
        config = RunConfig(
            model=model,
            tracing_disabled=not self.config.enable_tracing
        )

        # Create the agent with strict instructions to only use retrieved content and not hallucinate
        agent_instructions = (
            "You are a robotics expert assistant. "
            "You MUST ONLY use information from the retrieved content provided to you. "
            "Do NOT make up or hallucinate any information. "
            "If the retrieved content does not contain the answer to the user's question, "
            "you MUST clearly state that the information is not available in the provided content. "
            "Always cite your sources when providing information from the retrieved content. "
            "Be helpful but strict about only using the provided information."
        )

        # Create the agent with instructions for robotics expert and the retrieval tool
        agent = Agent(
            name="Robotics Expert Agent",
            instructions=agent_instructions,
            model=model,
            tools=[self.retrieve_robotics_content_tool],  # Add the retrieval tool to the agent
        )

        # Store the client as an instance variable to be used during run
        self.client = client

        return agent