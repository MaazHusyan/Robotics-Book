"""
Unit tests for the agent service components.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import List

from src.models.agent_models import (
    ChatSession, AgentConfig, ChatRequest, ChatResponse,
    AgentQuery, AgentResponse, AgentToolResult
)
from src.services.agent_service import AgentService, AgentServiceInterface
from src.services.rag_integration_service import RAGIntegrationService
from src.models.content_models import RetrievedContent


class TestAgentService:
    """Unit tests for the AgentService class."""

    @pytest.fixture
    def mock_rag_service(self):
        """Create a mock RAG integration service."""
        mock = MagicMock(spec=RAGIntegrationService)
        mock.get_relevant_content_for_query = AsyncMock()
        return mock

    @pytest.fixture
    def agent_config(self):
        """Create a default agent configuration."""
        return AgentConfig(
            model_name="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=1000,
            top_k=5,
            min_relevance_score=0.5,
            enable_tracing=False,
            timeout_seconds=30
        )

    @pytest.fixture
    def agent_service(self, mock_rag_service, agent_config):
        """Create an agent service instance with mocked dependencies."""
        return AgentService(config=agent_config, rag_service=mock_rag_service)

    @pytest.mark.asyncio
    async def test_process_message_valid_input(self, agent_service, mock_rag_service):
        """Test processing a valid message."""
        # Arrange
        message = "What is forward kinematics?"
        expected_content = [
            RetrievedContent(
                id="1", chunk_id="chunk1", content="Forward kinematics definition...",
                source_file="robotics_book.pdf", source_location="Chapter 3, Section 1",
                relevance_score=0.85
            )
        ]
        mock_rag_service.get_relevant_content_for_query.return_value = expected_content

        # Act
        result = await agent_service.process_message(message=message)

        # Assert
        assert result.session_id is not None
        assert result.query == message
        assert result.response is not None
        assert len(result.sources) == 1
        assert result.sources[0]["id"] == "1"
        assert result.has_relevant_content is True
        assert result.conversation_turn == 1

    @pytest.mark.asyncio
    async def test_process_message_with_session_id(self, agent_service, mock_rag_service):
        """Test processing a message with an existing session ID."""
        # Arrange
        session_id = "test-session-123"
        message = "What is inverse kinematics?"
        expected_content = [
            RetrievedContent(
                id="2", chunk_id="chunk2", content="Inverse kinematics definition...",
                source_file="robotics_book.pdf", source_location="Chapter 3, Section 2",
                relevance_score=0.78
            )
        ]
        mock_rag_service.get_relevant_content_for_query.return_value = expected_content

        # Act
        result = await agent_service.process_message(message=message, session_id=session_id)

        # Assert
        assert result.session_id == session_id
        assert result.query == message
        assert len(result.sources) == 1
        assert result.sources[0]["id"] == "2"

    @pytest.mark.asyncio
    async def test_process_message_no_relevant_content(self, agent_service, mock_rag_service):
        """Test processing a message when no relevant content is found."""
        # Arrange
        message = "What is the meaning of life?"
        mock_rag_service.get_relevant_content_for_query.return_value = []

        # Act
        result = await agent_service.process_message(message=message, require_sources=True)

        # Assert
        assert result.query == message
        assert len(result.sources) == 0
        assert result.has_relevant_content is False

    @pytest.mark.asyncio
    async def test_process_message_invalid_input(self, agent_service):
        """Test processing with invalid input."""
        # Test empty message
        with pytest.raises(ValueError):
            await agent_service.process_message(message="")

        # Test very short message
        with pytest.raises(ValueError):
            await agent_service.process_message(message="a")

        # Test very long message
        with pytest.raises(ValueError):
            long_message = "a" * 10001  # More than 10,000 characters
            await agent_service.process_message(message=long_message)

        # Test invalid temperature
        with pytest.raises(ValueError):
            await agent_service.process_message(
                message="What is robotics?",
                temperature=1.5  # Greater than 1.0
            )

        with pytest.raises(ValueError):
            await agent_service.process_message(
                message="What is robotics?",
                temperature=-0.5  # Less than 0.0
            )

        # Test invalid max_tokens
        with pytest.raises(ValueError):
            await agent_service.process_message(
                message="What is robotics?",
                max_tokens=0  # Not positive
            )

        with pytest.raises(ValueError):
            await agent_service.process_message(
                message="What is robotics?",
                max_tokens=-10  # Negative
            )

    @pytest.mark.asyncio
    async def test_process_message_rag_error(self, agent_service, mock_rag_service):
        """Test processing a message when RAG service fails."""
        # Arrange
        message = "What is path planning?"
        mock_rag_service.get_relevant_content_for_query.side_effect = Exception("RAG service unavailable")

        # Act
        result = await agent_service.process_message(message=message, require_sources=True)

        # Assert
        assert result.query == message
        assert len(result.sources) == 0
        assert result.error is not None
        assert "Retrieval error" in result.error

    def test_create_session(self, agent_service):
        """Test creating a new session."""
        # Act
        session = agent_service.create_session()

        # Assert - This will be an async method, so let's test the async version
        pass

    @pytest.mark.asyncio
    async def test_create_session_async(self, agent_service):
        """Test creating a new session asynchronously."""
        # Act
        session = await agent_service.create_session()

        # Assert
        assert session.session_id is not None
        assert session.created_at is not None
        assert session.updated_at is not None
        assert session.conversation_history == []
        assert len(agent_service.sessions) == 1
        assert session.session_id in agent_service.sessions

    @pytest.mark.asyncio
    async def test_get_session(self, agent_service):
        """Test getting an existing session."""
        # Arrange
        session = await agent_service.create_session()
        session_id = session.session_id

        # Act
        retrieved_session = await agent_service.get_session(session_id)

        # Assert
        assert retrieved_session is not None
        assert retrieved_session.session_id == session_id
        assert retrieved_session.created_at == session.created_at

    @pytest.mark.asyncio
    async def test_get_session_nonexistent(self, agent_service):
        """Test getting a non-existent session."""
        # Act
        retrieved_session = await agent_service.get_session("nonexistent-id")

        # Assert
        assert retrieved_session is None

    @pytest.mark.asyncio
    async def test_update_session(self, agent_service):
        """Test updating an existing session."""
        # Arrange
        session = await agent_service.create_session()
        original_updated_at = session.updated_at
        session.conversation_history.append({
            "role": "user",
            "content": "test message",
            "timestamp": datetime.now()
        })

        # Act
        success = await agent_service.update_session(session)

        # Assert
        assert success is True
        stored_session = agent_service.sessions[session.session_id]
        assert stored_session.conversation_history[0]["content"] == "test message"
        assert stored_session.updated_at > original_updated_at

    @pytest.mark.asyncio
    async def test_update_session_invalid(self, agent_service):
        """Test updating an invalid session."""
        # Act
        success = await agent_service.update_session(None)

        # Assert
        assert success is False

    @pytest.mark.asyncio
    async def test_clear_session(self, agent_service):
        """Test clearing an existing session."""
        # Arrange
        session = await agent_service.create_session()
        session_id = session.session_id
        assert session_id in agent_service.sessions

        # Act
        success = await agent_service.clear_session(session_id)

        # Assert
        assert success is True
        assert session_id not in agent_service.sessions

    @pytest.mark.asyncio
    async def test_clear_session_nonexistent(self, agent_service):
        """Test clearing a non-existent session."""
        # Act
        success = await agent_service.clear_session("nonexistent-id")

        # Assert
        assert success is False

    @pytest.mark.asyncio
    async def test_retrieve_robotics_content_success(self, agent_service, mock_rag_service):
        """Test the retrieve_robotics_content tool method."""
        # Arrange
        expected_content = [
            RetrievedContent(
                id="3", chunk_id="chunk3", content="Robot dynamics content...",
                source_file="robotics_book.pdf", source_location="Chapter 4, Section 1",
                relevance_score=0.92
            )
        ]
        mock_rag_service.get_relevant_content_for_query.return_value = expected_content

        # Act
        result = await agent_service.retrieve_robotics_content("robot dynamics")

        # Assert
        assert isinstance(result, AgentToolResult)
        assert result.tool_name == "retrieve_robotics_content"
        assert result.success is True
        assert len(result.content) == 1
        assert result.content[0]["id"] == "3"
        assert result.error is None

    @pytest.mark.asyncio
    async def test_retrieve_robotics_content_error(self, agent_service, mock_rag_service):
        """Test the retrieve_robotics_content tool method with error."""
        # Arrange
        mock_rag_service.get_relevant_content_for_query.side_effect = Exception("Retrieval failed")

        # Act
        result = await agent_service.retrieve_robotics_content("invalid query")

        # Assert
        assert isinstance(result, AgentToolResult)
        assert result.tool_name == "retrieve_robotics_content"
        assert result.success is False
        assert len(result.content) == 0
        assert result.error is not None


class TestAgentServiceInterface:
    """Tests for the AgentServiceInterface."""

    def test_interface_methods_exist(self):
        """Test that the interface defines the required methods."""
        # This test ensures that the interface has the required abstract methods
        interface = AgentServiceInterface()

        # Check that abstract methods exist
        assert hasattr(interface, 'process_message')
        assert hasattr(interface, 'create_session')
        assert hasattr(interface, 'get_session')
        assert hasattr(interface, 'update_session')
        assert hasattr(interface, 'clear_session')

        # Check that they are callable
        assert callable(getattr(interface, 'process_message'))
        assert callable(getattr(interface, 'create_session'))
        assert callable(getattr(interface, 'get_session'))
        assert callable(getattr(interface, 'update_session'))
        assert callable(getattr(interface, 'clear_session'))


if __name__ == "__main__":
    pytest.main([__file__])