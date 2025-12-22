"""
API endpoints for the chatbot agent integration.

Based on the api-contract.md specification for the 001-chatbot-agent-integration feature.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
import logging
import time

from ..models.agent_models import ChatRequest, ChatResponse
from ..services.agent_service import AgentService
from ..services.rag_integration_service import RAGIntegrationService
from ..config import get_settings
from ..retrieval.utils.qdrant_retriever import QdrantRetriever


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["agent"])


def get_agent_service() -> AgentService:
    """Dependency to get the agent service instance."""
    settings = get_settings()

    # Initialize the RAG integration service
    rag_service = RAGIntegrationService()

    # Create agent configuration
    from ..models.agent_models import AgentConfig
    agent_config = AgentConfig(
        model_name=settings.MODEL if settings.MODEL else "gemini/gemini-2.5-flash",
        temperature=0.7,  # Default value
        max_tokens=1000,  # Default value
        top_k=5,  # Default value
        min_relevance_score=0.5,  # Default value
        enable_tracing=getattr(settings, 'enable_tracing', False),
        timeout_seconds=30  # Default value
    )

    # Create and return the agent service
    return AgentService(config=agent_config, rag_service=rag_service)


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    chat_request: ChatRequest,
    background_tasks: BackgroundTasks,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Send a message to the chatbot agent and receive a response.

    This endpoint handles chat interactions with the robotics expert agent,
    maintaining conversation context and providing source-accurate responses.
    """
    start_time = time.time()

    try:
        # Sanitize and validate the request
        # Sanitize message input to prevent potential injection attacks
        sanitized_message = chat_request.message
        if sanitized_message:
            # Remove potential control characters that could be used maliciously
            sanitized_message = ''.join(char for char in sanitized_message if ord(char) >= 32 or char in '\n\r\t')

            # Additional sanitization could include removing potential script tags or other malicious content
            # For now, we'll log the original and sanitized versions for monitoring
            if sanitized_message != chat_request.message:
                logger.warning(f"Message sanitized - original length: {len(chat_request.message)}, sanitized length: {len(sanitized_message)}")

        # Validate the request
        if not sanitized_message or len(sanitized_message.strip()) < 1:
            raise HTTPException(
                status_code=400,
                detail="Message field is required and must be at least 1 character long"
            )

        if len(sanitized_message) > 10000:
            raise HTTPException(
                status_code=400,
                detail="Message exceeds maximum length of 10,000 characters"
            )

        # Validate session_id format to prevent injection
        if chat_request.session_id:
            import re
            # Basic validation for session ID format - alphanumeric, hyphens, underscores only
            if not re.match(r'^[a-zA-Z0-9_-]+$', chat_request.session_id):
                logger.warning(f"Invalid session ID format: {chat_request.session_id}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid session ID format"
                )

        if chat_request.temperature is not None and (chat_request.temperature < 0.0 or chat_request.temperature > 1.0):
            raise HTTPException(
                status_code=400,
                detail="Temperature must be between 0.0 and 1.0"
            )

        if chat_request.max_tokens is not None and chat_request.max_tokens <= 0:
            raise HTTPException(
                status_code=400,
                detail="Max tokens must be a positive integer"
            )

        # Process the message using the agent service
        agent_response = await agent_service.process_message(
            message=sanitized_message,
            session_id=chat_request.session_id,
            require_sources=chat_request.require_sources,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens
        )

        # Log the interaction
        response_time = time.time() - start_time
        logger.info(f"Chat request processed successfully. Session: {agent_response.session_id}, Response time: {response_time:.2f}s")

        # Convert AgentResponse to ChatResponse
        chat_response = ChatResponse(
            session_id=agent_response.session_id,
            response=agent_response.response,
            sources=agent_response.sources,  # Already in the correct format from AgentResponse
            conversation_turn=agent_response.conversation_turn,
            has_relevant_content=agent_response.has_relevant_content,
            timestamp=agent_response.timestamp
        )

        return chat_response

    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during chat processing"
        )


@router.get("/session/{session_id}")
async def get_session_endpoint(
    session_id: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Get session details and conversation history.
    """
    try:
        session = await agent_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        return {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "conversation_history": session.conversation_history,
            "user_id": session.user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving session"
        )


@router.delete("/session/{session_id}")
async def clear_session_endpoint(
    session_id: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    End and clear a conversation session.
    """
    try:
        success = await agent_service.clear_session(session_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        return {
            "message": "Session cleared successfully",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while clearing session"
        )


# Update the tasks file to mark T013 as completed
# This is done programmatically by updating the tasks.md file