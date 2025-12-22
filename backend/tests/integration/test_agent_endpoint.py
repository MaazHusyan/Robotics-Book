"""
Integration tests for the agent endpoint.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime

from src.models.agent_models import RetrievedContent
from src.services.rag_integration_service import RAGIntegrationService
from main import app  # Import the main app


class TestAgentEndpointIntegration:
    """Integration tests for the agent endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_chat_endpoint_success(self):
        """Test successful chat endpoint request."""
        # Mock the RAG service to avoid needing a real Qdrant instance
        with patch('src.api.agent_endpoint.get_agent_service') as mock_get_service:
            # Create a mock agent service
            mock_agent_service = AsyncMock()
            mock_agent_service.process_message = AsyncMock(return_value=type('obj', (object,), {
                'session_id': 'test-session-123',
                'query': 'What is forward kinematics?',
                'response': 'Forward kinematics is the process of determining the position...',
                'sources': [
                    {
                        'id': '1',
                        'chunk_id': 'chunk1',
                        'content': 'Forward kinematics definition from robotics book...',
                        'source_file': 'robotics_book.pdf',
                        'source_location': 'Chapter 3, Section 1',
                        'relevance_score': 0.85
                    }
                ],
                'conversation_turn': 1,
                'timestamp': datetime.now(),
                'response_time': 1.23,
                'has_relevant_content': True,
                'error': None
            })())

            # Create a mock config
            mock_config = type('obj', (object,), {
                'model_name': 'gemini-2.5-flash',
                'temperature': 0.7,
                'max_tokens': 1000,
                'top_k': 5,
                'min_relevance_score': 0.5,
                'enable_tracing': False,
                'timeout_seconds': 30
            })()

            # Mock the get_agent_service function to return our mock service
            mock_rag_service = AsyncMock()
            mock_get_service.return_value = mock_agent_service

            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/chat",
                    json={
                        "message": "What is forward kinematics?",
                        "session_id": None,
                        "require_sources": True
                    },
                    headers={"Content-Type": "application/json"}
                )

                assert response.status_code == 200
                data = response.json()
                assert "session_id" in data
                assert "response" in data
                assert "sources" in data
                assert data["has_relevant_content"] is True

    @pytest.mark.asyncio
    async def test_chat_endpoint_with_session(self):
        """Test chat endpoint with an existing session."""
        with patch('src.api.agent_endpoint.get_agent_service') as mock_get_service:
            mock_agent_service = AsyncMock()
            mock_agent_service.process_message = AsyncMock(return_value=type('obj', (object,), {
                'session_id': 'existing-session-456',
                'query': 'Can you elaborate?',
                'response': 'Certainly, forward kinematics involves calculating...',
                'sources': [
                    {
                        'id': '2',
                        'chunk_id': 'chunk2',
                        'content': 'Detailed explanation of forward kinematics...',
                        'source_file': 'robotics_book.pdf',
                        'source_location': 'Chapter 3, Section 2',
                        'relevance_score': 0.78
                    }
                ],
                'conversation_turn': 2,
                'timestamp': datetime.now(),
                'response_time': 0.95,
                'has_relevant_content': True,
                'error': None
            })())

            mock_get_service.return_value = mock_agent_service

            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/chat",
                    json={
                        "message": "Can you elaborate?",
                        "session_id": "existing-session-456",
                        "require_sources": True
                    },
                    headers={"Content-Type": "application/json"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["session_id"] == "existing-session-456"
                assert data["conversation_turn"] == 2

    def test_chat_endpoint_invalid_input(self):
        """Test chat endpoint with invalid input."""
        with TestClient(app) as client:
            # Test with empty message
            response = client.post(
                "/api/v1/chat",
                json={
                    "message": "",
                    "session_id": None
                },
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 400

            # Test with very long message
            response = client.post(
                "/api/v1/chat",
                json={
                    "message": "a" * 10001,  # More than 10,000 characters
                    "session_id": None
                },
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 400

            # Test with invalid temperature
            response = client.post(
                "/api/v1/chat",
                json={
                    "message": "What is robotics?",
                    "session_id": None,
                    "temperature": 1.5  # Greater than 1.0
                },
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_chat_endpoint_rag_error(self):
        """Test chat endpoint when RAG service fails."""
        with patch('src.api.agent_endpoint.get_agent_service') as mock_get_service:
            mock_agent_service = AsyncMock()
            # Simulate an error in process_message
            mock_agent_service.process_message.side_effect = Exception("RAG service unavailable")

            mock_get_service.return_value = mock_agent_service

            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/chat",
                    json={
                        "message": "What is forward kinematics?",
                        "session_id": None,
                        "require_sources": True
                    },
                    headers={"Content-Type": "application/json"}
                )

                # Should return 500 error since it's an internal server error
                assert response.status_code == 500

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "service" in data

    def test_root_endpoint(self):
        """Test the root endpoint."""
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "status" in data
            assert data["status"] == "healthy"


class TestAgentEndpointSecurity:
    """Security tests for the agent endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_chat_endpoint_input_sanitization(self):
        """Test that input sanitization works properly."""
        with TestClient(app) as client:
            # Test with message containing potential control characters
            response = client.post(
                "/api/v1/chat",
                json={
                    "message": "What is robotics?\x00\x01",  # Null and start of heading control chars
                    "session_id": None
                },
                headers={"Content-Type": "application/json"}
            )
            # Should still process successfully but with sanitized input
            assert response.status_code in [200, 400]  # Either success or validation error, but not crash

    def test_chat_endpoint_invalid_session_id_format(self):
        """Test chat endpoint with invalid session ID format."""
        with TestClient(app) as client:
            # Test with session ID containing potentially malicious characters
            response = client.post(
                "/api/v1/chat",
                json={
                    "message": "What is robotics?",
                    "session_id": "<script>alert('xss')</script>"  # XSS attempt
                },
                headers={"Content-Type": "application/json"}
            )
            # Should return 400 due to invalid session ID format validation
            assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__])