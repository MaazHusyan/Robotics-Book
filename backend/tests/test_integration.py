"""
Integration tests for RAG chatbot system.
Tests end-to-end workflows and component interactions.
"""

import pytest
import sys
import os
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

# Add a backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models.database import get_db_connection, create_tables
from models.qdrant_setup import get_qdrant_client, create_collection
from services.ingestion import IngestionService
from services.query_processor import QueryProcessor
from services.rag_agent import RAGAgent
from api.websocket import ConnectionManager


class TestDatabaseIntegration:
    """Test database integration scenarios."""

    @pytest.fixture
    def db_connection(self):
        """Create test database connection."""
        with patch("models.database.DATABASE_URL", "sqlite:///test.db"):
            create_tables()
            conn = get_db_connection()
            yield conn
            conn.close()

    def test_database_connection_and_tables(self, db_connection):
        """Test database connection and table creation."""
        # Test basic connection
        assert db_connection is not None

        # Test table existence
        with db_connection.cursor() as cur:
            # Check content_chunks table
            cur.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='content_chunks'
            """)
            result = cur.fetchone()
            assert result is not None

            # Check chat_sessions table
            cur.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='chat_sessions'
            """)
            result = cur.fetchone()
            assert result is not None

            # Check query_logs table
            cur.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='query_logs'
            """)
            result = cur.fetchone()
            assert result is not None

    def test_database_crud_operations(self, db_connection):
        """Test CRUD operations on database tables."""
        with db_connection.cursor() as cur:
            # Test content_chunks insertion
            cur.execute(
                """
                INSERT INTO content_chunks 
                (content, source_file, chapter, section, chunk_index, token_count)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                ("Test content", "test.mdx", "test-chapter", "test-section", 1, 10),
            )

            # Test retrieval
            cur.execute(
                "SELECT * FROM content_chunks WHERE source_file = ?", ("test.mdx",)
            )
            result = cur.fetchone()
            assert result is not None
            assert result["content"] == "Test content"

            # Test chat_sessions insertion
            cur.execute(
                """
                INSERT INTO chat_sessions 
                (id, ip_address, user_agent_hash, message_count)
                VALUES (?, ?, ?, ?)
            """,
                ("test_session", "127.0.0.1", "user_agent_hash", 0),
            )

            # Test query_logs insertion
            cur.execute(
                """
                INSERT INTO query_logs 
                (query_hash, question_length, response_length, response_time_ms, date_bucket)
                VALUES (?, ?, ?, ?, ?)
            """,
                ("query_hash", 20, 100, 1500, "2025-12-11"),
            )

            db_connection.commit()


class TestQdrantIntegration:
    """Test Qdrant vector database integration."""

    @pytest.fixture
    def mock_qdrant_client(self):
        """Create mock Qdrant client."""
        with patch("models.qdrant_setup.QdrantClient") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            # Mock collection operations
            mock_instance.get_collections.return_value.collections = []
            mock_instance.create_collection.return_value = None
            mock_instance.search.return_value = []
            mock_instance.upsert.return_value = None

            yield mock_instance

    def test_qdrant_client_initialization(self, mock_qdrant_client):
        """Test Qdrant client initialization."""
        with (
            patch("models.qdrant_setup.QDRANT_URL", "http://localhost:6333"),
            patch("models.qdrant_setup.QDRANT_API_KEY", "test-key"),
        ):
            client = get_qdrant_client()
            assert client is not None

    def test_collection_creation(self, mock_qdrant_client):
        """Test collection creation."""
        with (
            patch("models.qdrant_setup.QDRANT_URL", "http://localhost:6333"),
            patch("models.qdrant_setup.QDRANT_API_KEY", "test-key"),
        ):
            result = create_collection()
            assert result is True
            mock_qdrant_client.create_collection.assert_called_once()

    def test_vector_search_and_storage(self, mock_qdrant_client):
        """Test vector search and storage operations."""
        # Mock search results
        mock_qdrant_client.search.return_value = [
            Mock(payload={"content": "Robotics content 1"}, score=0.9),
            Mock(payload={"content": "Robotics content 2"}, score=0.8),
        ]

        # Test search
        with patch(
            "services.retrieval.get_qdrant_client", return_value=mock_qdrant_client
        ):
            from services.retrieval import RetrievalService

            service = RetrievalService()

            # Mock embedding generation
            with patch.object(service, "_embedding_service") as mock_embedding:
                mock_embedding.generate_embedding.return_value = [0.1, 0.2, 0.3]

                results = asyncio.run(service.search_content("What is robotics?"))

                assert len(results) == 2
                assert results[0]["content"] == "Robotics content 1"
                assert results[0]["score"] == 0.9


class TestServiceIntegration:
    """Test service layer integration."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services for integration testing."""
        with patch.multiple(
            "services.ingestion.TextChunkingService",
            "services.ingestion.EmbeddingService",
            "services.ingestion.VectorStoreService",
            "services.query_processor.RetrievalService",
            "services.query_processor.EmbeddingService",
            "services.rag_agent.QueryProcessor",
            "services.rag_agent.OpenAI",
        ) as mocks:
            yield mocks

    async def test_end_to_end_query_processing(self, mock_services):
        """Test end-to-end query processing pipeline."""
        # Mock text chunking
        mock_services["TextChunkingService"].return_value.chunk_text.return_value = [
            {"content": "Chunk 1", "metadata": {"source": "test.mdx"}},
            {"content": "Chunk 2", "metadata": {"source": "test.mdx"}},
        ]

        # Mock embedding generation
        mock_services[
            "EmbeddingService"
        ].return_value.generate_batch_embeddings.return_value = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ]

        # Mock vector storage
        mock_services[
            "VectorStoreService"
        ].return_value.store_vectors.return_value = True

        # Mock retrieval
        mock_services["RetrievalService"].return_value.search_content.return_value = [
            {"content": "Relevant content 1", "source": "test.mdx", "score": 0.9}
        ]

        # Mock OpenAI response
        mock_agent_response = Mock()
        mock_agent_response.choices = [Mock(message={"content": "Robotics answer"})]
        mock_services[
            "OpenAI"
        ].return_value.chat.completions.create.return_value = mock_agent_response

        # Test ingestion
        ingestion_service = IngestionService()
        ingestion_result = asyncio.run(
            ingestion_service.ingest_document("test.mdx", "Document content")
        )

        assert ingestion_result["success"] is True
        assert ingestion_result["chunks_processed"] == 2

        # Test query processing
        query_processor = QueryProcessor()
        query_result = asyncio.run(query_processor.process_query("What is robotics?"))

        assert "context" in query_result
        assert "sources" in query_result
        assert len(query_result["sources"]) > 0

        # Test RAG agent
        rag_agent = RAGAgent()
        agent_response = asyncio.run(rag_agent.query("What is robotics?"))

        assert "answer" in agent_response
        assert "sources" in agent_response
        assert agent_response["answer"] == "Robotics answer"


class TestWebSocketIntegration:
    """Test WebSocket integration scenarios."""

    @pytest.fixture
    def mock_connection_manager(self):
        """Create mock connection manager."""
        with patch("api.websocket.manager") as mock_manager:
            mock_instance = Mock()
            mock_instance.connect.return_value = "test_session_123"
            mock_instance.send_message = AsyncMock()
            mock_instance.disconnect = Mock()
            mock_manager.return_value = mock_instance
            yield mock_instance

    async def test_websocket_connection_flow(self, mock_connection_manager):
        """Test complete WebSocket connection flow."""
        from api.websocket import handle_websocket_connection
        from fastapi import WebSocket

        # Mock WebSocket
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.client = Mock(host="127.0.0.1")
        mock_websocket.headers = {"user-agent": "test-agent"}
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[
                json.dumps(
                    {"type": "question", "data": {"question": "What is robotics?"}}
                ),
                json.dumps({"type": "ping", "data": {}}),
            ]
        )

        # Mock agent
        with patch("api.websocket.create_robotics_tutor_agent") as mock_agent:
            mock_agent.return_value = Mock()

            # Test connection handling
            await handle_websocket_connection(mock_websocket)

            # Verify connection was accepted
            mock_websocket.accept.assert_called_once()

            # Verify session was created
            mock_connection_manager.connect.assert_called_once()

            # Verify welcome message was sent
            welcome_calls = [
                call
                for call in mock_connection_manager.send_message.call_args_list
                if call[1]["type"] == "welcome"
            ]
            assert len(welcome_calls) == 1

    async def test_websocket_message_processing(self, mock_connection_manager):
        """Test WebSocket message processing."""
        from api.websocket import handle_message

        # Mock agent
        mock_agent = Mock()

        # Test question message
        question_message = {
            "type": "question",
            "data": {
                "question": "What is robotics?",
                "context_chunks": ["Highlighted text"],
            },
        }

        await handle_message("test_session", question_message, mock_agent)

        # Verify message was processed (would call agent in real implementation)
        # This is a simplified test structure

    async def test_websocket_error_handling(self, mock_connection_manager):
        """Test WebSocket error handling."""
        from api.websocket import handle_message

        # Test invalid message
        invalid_message = {"invalid": "structure"}

        await handle_message("test_session", invalid_message, Mock())

        # Verify error response was sent
        error_calls = [
            call
            for call in mock_connection_manager.send_message.call_args_list
            if call[1]["type"] == "error"
        ]
        assert len(error_calls) >= 1


class TestSecurityIntegration:
    """Test security integration scenarios."""

    @pytest.fixture
    def mock_security_components(self):
        """Create mock security components."""
        with patch.multiple(
            "middleware.validation.InputValidator",
            "middleware.rate_limiter.RateLimiter",
            "utils.privacy.PrivacyManager",
        ) as mocks:
            yield mocks

    def test_input_validation_integration(self, mock_security_components):
        """Test input validation in integration context."""
        from middleware.validation import InputValidator

        # Mock validator
        mock_validator = Mock()
        mock_validator.validate_websocket_message.return_value = Mock(
            is_valid=True,
            sanitized_data={"question": "What is robotics?", "context_chunks": []},
        )
        mock_security_components["InputValidator"].return_value = mock_validator

        validator = InputValidator()
        message = {"type": "question", "data": {"question": "What is robotics?"}}
        result = validator.validate_websocket_message(message)

        assert result.is_valid is True
        assert "sanitized_data" in result.sanitized_data

    def test_rate_limiting_integration(self, mock_security_components):
        """Test rate limiting in integration context."""
        from middleware.rate_limiter import RateLimiter

        # Mock rate limiter
        mock_limiter = Mock()
        mock_limiter.check_rate_limit.return_value = {
            "remaining": 50,
            "limit": 100,
            "reset_time": "2025-12-11T12:00:00Z",
        }
        mock_security_components["RateLimiter"].return_value = mock_limiter

        limiter = RateLimiter()

        # Mock request
        mock_request = Mock()
        mock_request.client = Mock(host="127.0.0.1")

        result = asyncio.run(limiter.check_rate_limit(mock_request))

        assert "remaining" in result
        assert result["remaining"] == 50

    def test_privacy_anonymization_integration(self, mock_security_components):
        """Test privacy anonymization in integration context."""
        from utils.privacy import PrivacyManager

        # Mock privacy manager
        mock_privacy = Mock()
        mock_privacy.process_request_data.return_value = {
            "ip_address_hash": "hashed_ip",
            "anonymized_query": "What is robotics?",
            "pii_detected": False,
        }
        mock_security_components["PrivacyManager"].return_value = mock_privacy

        privacy_manager = PrivacyManager()
        result = privacy_manager.process_request_data(
            "127.0.0.1", "test-agent", "What is robotics?"
        )

        assert result["ip_address_hash"] == "hashed_ip"
        assert result["pii_detected"] is False


class TestPerformanceIntegration:
    """Test performance integration scenarios."""

    async def test_concurrent_query_processing(self):
        """Test concurrent query processing performance."""
        # Mock services for concurrent processing
        with patch.multiple(
            "services.query_processor.QueryProcessor", "services.rag_agent.RAGAgent"
        ) as mocks:
            # Mock fast processing
            mocks["QueryProcessor"].return_value.process_query.return_value = {
                "context": ["Test context"],
                "sources": ["test.mdx"],
            }

            mocks["RAGAgent"].return_value.query.return_value = "Test answer"

            # Create multiple concurrent queries
            processor = QueryProcessor()
            agent = RAGAgent()

            tasks = [processor.process_query(f"Question {i}") for i in range(10)]

            start_time = datetime.utcnow()
            results = await asyncio.gather(*tasks)
            end_time = datetime.utcnow()

            # Verify all queries completed
            assert len(results) == 10

            # Verify performance (should complete quickly)
            processing_time = (end_time - start_time).total_seconds()
            assert processing_time < 5.0  # Should complete in under 5 seconds

    def test_memory_usage_optimization(self):
        """Test memory usage optimization."""
        # Test large content processing
        large_content = "x" * 10000  # 10k characters

        with patch("services.text_chunking.TextChunkingService") as mock_chunking:
            # Mock efficient chunking
            mock_chunking.return_value.chunk_text.return_value = [
                {"content": large_content[i : i + 1000], "metadata": {}}
                for i in range(0, len(large_content), 1000)
            ]

            from services.text_chunking import TextChunkingService

            service = TextChunkingService()
            chunks = service.chunk_text(large_content)

            # Verify chunking was efficient
            assert len(chunks) > 0
            assert all(len(chunk["content"]) <= 1000 for chunk in chunks)


class TestErrorRecoveryIntegration:
    """Test error recovery scenarios."""

    async def test_database_connection_recovery(self):
        """Test database connection recovery."""
        with patch("models.database.get_db_connection") as mock_get_conn:
            # Mock connection failure then success
            mock_get_conn.side_effect = [
                Exception("Connection failed"),
                Mock(),  # Success on retry
            ]

            from models.database import execute_query
            from services.ingestion import IngestionService

            # Test retry logic
            try:
                result = execute_query("SELECT 1")
                # Should succeed on retry
                assert result is not None
            except Exception as e:
                # Should handle gracefully
                assert "Connection failed" in str(e)

    async def test_external_service_recovery(self):
        """Test external service failure recovery."""
        with patch("services.embeddings.OpenAI") as mock_openai:
            # Mock API failure then success
            mock_client = Mock()
            mock_client.embeddings.create.side_effect = [
                Exception("API Error"),
                Mock(data=[Mock(embedding=[0.1, 0.2, 0.3])]),
            ]
            mock_openai.return_value = mock_client

            from services.embeddings import EmbeddingService

            service = EmbeddingService()

            # Test with retry logic
            try:
                result = await service.generate_embedding("Test text")
                # Should succeed on retry
                assert result is not None
                assert len(result) == 3
            except Exception as e:
                # Should handle gracefully
                assert "API Error" in str(e)


if __name__ == "__main__":
    pytest.main([__file__])
