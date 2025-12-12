"""
Unit tests for RAG chatbot services.
Tests all service modules for functionality and error handling.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import asyncio

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from services.content_validator import ContentValidator
from services.context_manager import ContextManager
from services.embeddings import EmbeddingService
from services.ingestion import IngestionService
from services.query_processor import QueryProcessor
from services.rag_agent import RAGAgent
from services.response_streamer import ResponseStreamer
from services.retrieval import RetrievalService
from services.text_chunking import TextChunkingService
from services.vector_store import VectorStoreService
from services.parallel_processor import ParallelProcessor


class TestContentValidator:
    """Test ContentValidator service."""

    def test_validate_question_valid(self):
        """Test validating a valid question."""
        validator = ContentValidator()
        result = validator.validate_question("What is robotics?")

        assert result.is_valid is True
        assert result.errors == []
        assert "sanitized_question" in result.sanitized_data

    def test_validate_question_empty(self):
        """Test validating an empty question."""
        validator = ContentValidator()
        result = validator.validate_question("")

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "empty" in " ".join(result.errors).lower()

    def test_validate_question_too_long(self):
        """Test validating a question that's too long."""
        validator = ContentValidator()
        long_question = "x" * 1001
        result = validator.validate_question(long_question)

        assert result.is_valid is False
        assert any("too long" in error.lower() for error in result.errors)

    def test_validate_context_chunks_valid(self):
        """Test validating valid context chunks."""
        validator = ContentValidator()
        chunks = ["Chunk 1 content", "Chunk 2 content"]
        result = validator.validate_context_chunks(chunks)

        assert result.is_valid is True
        assert result.errors == []
        assert "context_chunks" in result.sanitized_data

    def test_validate_context_chunks_too_many(self):
        """Test validating too many context chunks."""
        validator = ContentValidator()
        chunks = [f"Chunk {i}" for i in range(10)]  # More than allowed
        result = validator.validate_context_chunks(chunks)

        assert result.is_valid is False
        assert any("too many" in error.lower() for error in result.errors)


class TestContextManager:
    """Test ContextManager service."""

    def test_context_manager_initialization(self):
        """Test ContextManager initialization."""
        manager = ContextManager()
        assert manager is not None
        assert hasattr(manager, "contexts")

    def test_add_context(self):
        """Test adding context to manager."""
        manager = ContextManager()
        session_id = "test_session"
        context_data = {"chunks": ["chunk1", "chunk2"], "timestamp": datetime.utcnow()}

        manager.add_context(session_id, context_data)

        retrieved = manager.get_context(session_id)
        assert retrieved is not None
        assert retrieved["chunks"] == ["chunk1", "chunk2"]

    def test_remove_context(self):
        """Test removing context from manager."""
        manager = ContextManager()
        session_id = "test_session"
        context_data = {"chunks": ["chunk1"]}

        manager.add_context(session_id, context_data)
        assert manager.get_context(session_id) is not None

        manager.remove_context(session_id)
        assert manager.get_context(session_id) is None

    def test_cleanup_expired_contexts(self):
        """Test cleanup of expired contexts."""
        manager = ContextManager()
        old_time = datetime.utcnow() - timedelta(hours=2)

        manager.add_context("old_session", {"chunks": [], "timestamp": old_time})
        manager.add_context(
            "new_session", {"chunks": [], "timestamp": datetime.utcnow()}
        )

        # Simulate cleanup (1 hour expiration)
        manager.cleanup_expired_contexts(max_age_hours=1)

        assert manager.get_context("old_session") is None
        assert manager.get_context("new_session") is not None


class TestEmbeddingService:
    """Test EmbeddingService."""

    @patch("services.embeddings.OpenAI")
    def test_generate_embedding_success(self, mock_openai):
        """Test successful embedding generation."""
        # Mock OpenAI response
        mock_client = Mock()
        mock_client.embeddings.create.return_value = Mock(
            data=[Mock(embedding=[0.1, 0.2, 0.3])]
        )
        mock_openai.return_value = mock_client

        service = EmbeddingService()
        result = asyncio.run(service.generate_embedding("Test text"))

        assert result is not None
        assert len(result) == 3
        assert result[0] == 0.1

    @patch("services.embeddings.OpenAI")
    def test_generate_embedding_api_error(self, mock_openai):
        """Test embedding generation with API error."""
        mock_client = Mock()
        mock_client.embeddings.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        service = EmbeddingService()

        with pytest.raises(Exception):
            asyncio.run(service.generate_embedding("Test text"))

    def test_batch_embedding_generation(self):
        """Test batch embedding generation."""
        service = EmbeddingService()
        texts = ["Text 1", "Text 2", "Text 3"]

        # Mock the batch generation
        with patch.object(service, "generate_embedding") as mock_generate:
            mock_generate.return_value = [0.1, 0.2, 0.3]

            results = asyncio.run(service.generate_batch_embeddings(texts))

            assert len(results) == 3
            assert mock_generate.call_count == 3


class TestRetrievalService:
    """Test RetrievalService."""

    @patch("services.retrieval.QdrantClient")
    @patch("services.retrieval.EmbeddingService")
    def test_search_content_success(self, mock_embedding_service, mock_qdrant):
        """Test successful content search."""
        # Mock embedding service
        mock_embedding_service.return_value.generate_embedding.return_value = [0.1, 0.2]

        # Mock Qdrant response
        mock_client = Mock()
        mock_client.search.return_value = [
            Mock(
                payload={"content": "Robotics content 1", "source_file": "test1.mdx"},
                score=0.9,
            ),
            Mock(
                payload={"content": "Robotics content 2", "source_file": "test2.mdx"},
                score=0.8,
            ),
        ]
        mock_qdrant.return_value = mock_client

        service = RetrievalService()
        results = asyncio.run(service.search_content("What is robotics?"))

        assert len(results) == 2
        assert results[0]["content"] == "Robotics content 1"
        assert results[0]["score"] == 0.9

    @patch("services.retrieval.QdrantClient")
    def test_search_content_no_results(self, mock_qdrant):
        """Test content search with no results."""
        mock_client = Mock()
        mock_client.search.return_value = []
        mock_qdrant.return_value = mock_client

        service = RetrievalService()
        results = asyncio.run(service.search_content("Nonexistent topic"))

        assert len(results) == 0

    def test_search_with_threshold(self):
        """Test search with similarity threshold."""
        service = RetrievalService()

        with patch.object(service, "_client") as mock_client:
            mock_client.search.return_value = [
                Mock(payload={"content": "Low similarity"}, score=0.5),
                Mock(payload={"content": "High similarity"}, score=0.9),
            ]

            results = asyncio.run(service.search_content("test query", threshold=0.7))

            assert len(results) == 1
            assert results[0]["content"] == "High similarity"


class TestTextChunkingService:
    """Test TextChunkingService."""

    def test_chunk_text_basic(self):
        """Test basic text chunking."""
        service = TextChunkingService()
        text = "x" * 1000  # 1000 characters

        chunks = service.chunk_text(text)

        assert len(chunks) > 0
        assert all(len(chunk) <= 1000 for chunk in chunks)
        assert all(len(chunk) >= 500 for chunk in chunks[:-1])  # All but last

    def test_chunk_text_with_overlap(self):
        """Test text chunking with overlap."""
        service = TextChunkingService(chunk_size=800, overlap=200)
        text = "x" * 2000

        chunks = service.chunk_text(text)

        assert len(chunks) >= 2
        # Check overlap exists
        for i in range(len(chunks) - 1):
            end_of_chunk1 = chunks[i][-200:]
            start_of_chunk2 = chunks[i + 1][:200]
            assert end_of_chunk1 == start_of_chunk2

    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        service = TextChunkingService()
        chunks = service.chunk_text("")

        assert len(chunks) == 0

    def test_chunk_short_text(self):
        """Test chunking text shorter than chunk size."""
        service = TextChunkingService()
        text = "x" * 100  # Shorter than default chunk size

        chunks = service.chunk_text(text)

        assert len(chunks) == 1
        assert chunks[0] == text


class TestVectorStoreService:
    """Test VectorStoreService."""

    @patch("services.vector_store.QdrantClient")
    def test_store_vectors_success(self, mock_qdrant):
        """Test successful vector storage."""
        mock_client = Mock()
        mock_client.upsert.return_value = Mock(status="completed")
        mock_qdrant.return_value = mock_client

        service = VectorStoreService()
        vectors = [
            {"id": "vec1", "vector": [0.1, 0.2], "payload": {"content": "test1"}},
            {"id": "vec2", "vector": [0.3, 0.4], "payload": {"content": "test2"}},
        ]

        result = asyncio.run(service.store_vectors(vectors))

        assert result is True
        assert mock_client.upsert.call_count == 1

    @patch("services.vector_store.QdrantClient")
    def test_store_vectors_failure(self, mock_qdrant):
        """Test vector storage failure."""
        mock_client = Mock()
        mock_client.upsert.side_effect = Exception("Storage failed")
        mock_qdrant.return_value = mock_client

        service = VectorStoreService()
        vectors = [{"id": "vec1", "vector": [0.1, 0.2]}]

        with pytest.raises(Exception):
            asyncio.run(service.store_vectors(vectors))

    @patch("services.vector_store.QdrantClient")
    def test_delete_vectors(self, mock_qdrant):
        """Test vector deletion."""
        mock_client = Mock()
        mock_client.delete.return_value = Mock(status="completed")
        mock_qdrant.return_value = mock_client

        service = VectorStoreService()
        vector_ids = ["vec1", "vec2"]

        result = asyncio.run(service.delete_vectors(vector_ids))

        assert result is True
        mock_client.delete.assert_called_once()


class TestParallelProcessor:
    """Test ParallelProcessor service."""

    def test_process_tasks_parallel(self):
        """Test parallel processing of tasks."""
        processor = ParallelProcessor()

        async def dummy_task(x):
            await asyncio.sleep(0.1)
            return x * 2

        tasks = [dummy_task(i) for i in range(5)]
        results = asyncio.run(processor.process_parallel(tasks))

        assert len(results) == 5
        assert results == [0, 2, 4, 6, 8]

    def test_process_tasks_with_error(self):
        """Test parallel processing with errors."""
        processor = ParallelProcessor()

        async def failing_task(x):
            if x == 3:
                raise ValueError("Task failed")
            await asyncio.sleep(0.1)
            return x * 2

        tasks = [failing_task(i) for i in range(5)]

        with pytest.raises(ValueError):
            asyncio.run(processor.process_parallel(tasks))

    def test_process_tasks_with_timeout(self):
        """Test parallel processing with timeout."""
        processor = ParallelProcessor()

        async def slow_task(x):
            await asyncio.sleep(2.0)  # Longer than timeout
            return x * 2

        tasks = [slow_task(i) for i in range(3)]

        results = asyncio.run(processor.process_parallel(tasks, timeout=1.0))

        # Should handle timeout gracefully
        assert len(results) <= 3


class TestQueryProcessor:
    """Test QueryProcessor service."""

    @patch("services.query_processor.RetrievalService")
    @patch("services.query_processor.EmbeddingService")
    def test_process_query_success(self, mock_embedding, mock_retrieval):
        """Test successful query processing."""
        # Mock embedding
        mock_embedding.return_value.generate_embedding.return_value = [0.1, 0.2, 0.3]

        # Mock retrieval
        mock_retrieval.return_value.search_content.return_value = [
            {"content": "Robotics answer", "source": "test.mdx", "score": 0.9}
        ]

        processor = QueryProcessor()
        result = asyncio.run(processor.process_query("What is robotics?"))

        assert result["query"] == "What is robotics?"
        assert "context" in result
        assert "sources" in result
        assert len(result["sources"]) > 0

    def test_process_query_with_context(self):
        """Test query processing with additional context."""
        processor = QueryProcessor()

        with patch.object(processor, "_retrieval_service") as mock_retrieval:
            mock_retrieval.search_content.return_value = []

            result = asyncio.run(
                processor.process_query(
                    "What about this?",
                    context_chunks=["Highlighted text 1", "Highlighted text 2"],
                )
            )

            assert "context" in result
            assert len(result["context"]) >= 2


class TestResponseStreamer:
    """Test ResponseStreamer service."""

    async def test_stream_response_chunks(self):
        """Test streaming response in chunks."""
        streamer = ResponseStreamer()
        response_text = (
            "This is a long response that should be streamed in multiple chunks."
        )

        chunks = []

        async def collect_chunks():
            async for chunk in streamer.stream_response(response_text, chunk_size=10):
                chunks.append(chunk)

        await collect_chunks()

        assert len(chunks) > 1
        assert "".join(chunks) == response_text

    async def test_stream_response_with_delay(self):
        """Test streaming response with delay."""
        streamer = ResponseStreamer()
        response_text = "Test response"

        start_time = datetime.utcnow()
        chunks = []

        async def collect_chunks():
            async for chunk in streamer.stream_response(
                response_text, chunk_size=5, delay=0.01
            ):
                chunks.append(chunk)

        await collect_chunks()
        end_time = datetime.utcnow()

        assert (end_time - start_time).total_seconds() >= 0.02  # At least 2 delays
        assert len(chunks) == 3  # "Test ", "respon", "se"


class TestIngestionService:
    """Test IngestionService."""

    @patch("services.ingestion.TextChunkingService")
    @patch("services.ingestion.EmbeddingService")
    @patch("services.ingestion.VectorStoreService")
    def test_ingest_document_success(
        self, mock_vector_store, mock_embedding, mock_chunking
    ):
        """Test successful document ingestion."""
        # Mock chunking
        mock_chunking.return_value.chunk_text.return_value = [
            {"content": "Chunk 1", "metadata": {"source": "test.mdx"}},
            {"content": "Chunk 2", "metadata": {"source": "test.mdx"}},
        ]

        # Mock embedding
        mock_embedding.return_value.generate_batch_embeddings.return_value = [
            [0.1, 0.2],
            [0.3, 0.4],
        ]

        # Mock vector storage
        mock_vector_store.return_value.store_vectors.return_value = True

        service = IngestionService()
        result = asyncio.run(
            service.ingest_document("test.mdx", "Document content here")
        )

        assert result["success"] is True
        assert result["chunks_processed"] == 2
        assert result["vectors_stored"] == 2

    def test_ingest_document_not_found(self):
        """Test ingestion of non-existent document."""
        service = IngestionService()

        with pytest.raises(FileNotFoundError):
            asyncio.run(service.ingest_document("nonexistent.mdx", "content"))


class TestRAGAgent:
    """Test RAGAgent service."""

    @patch("services.rag_agent.QueryProcessor")
    @patch("services.rag_agent.OpenAI")
    def test_agent_query_response(self, mock_openai, mock_query_processor):
        """Test agent query and response generation."""
        # Mock query processor
        mock_query_processor.return_value.process_query.return_value = {
            "context": ["Relevant context"],
            "sources": ["source1.mdx"],
        }

        # Mock OpenAI
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message={"content": "Robotics answer"})]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        agent = RAGAgent()
        response = asyncio.run(agent.query("What is robotics?"))

        assert "answer" in response
        assert "sources" in response
        assert response["answer"] == "Robotics answer"

    def test_agent_with_no_context(self):
        """Test agent behavior with no available context."""
        agent = RAGAgent()

        with patch.object(agent, "_query_processor") as mock_processor:
            mock_processor.process_query.return_value = {"context": [], "sources": []}

            response = asyncio.run(agent.query("Question about unknown topic"))

            assert "answer" in response
            # Should handle no context gracefully


if __name__ == "__main__":
    pytest.main([__file__])
