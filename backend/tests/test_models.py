"""
Unit tests for RAG chatbot models.
Tests ContentChunk, ChatSession, QueryLog and ChatMessage entities.
"""

import pytest
import uuid
import sys
import os
from datetime import datetime, timedelta
from pydantic import ValidationError

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models.entities import (
    ContentChunk,
    ChatSession,
    QueryLog,
    ChatMessage,
    ChunkType,
    MessageType,
)


class TestContentChunk:
    """Test ContentChunk model validation and behavior."""

    def test_valid_content_chunk_creation(self):
        """Test creating a valid ContentChunk."""
        chunk = ContentChunk(
            content="This is a valid content chunk that meets the length requirements.",
            source_file="01-introduction/01-history.mdx",
            chapter="01-introduction",
            section="01-history",
            chunk_index=0,
            token_count=15,
            chunk_type=ChunkType.PARAGRAPH,
        )

        assert chunk.id is not None
        assert (
            chunk.content
            == "This is a valid content chunk that meets the length requirements."
        )
        assert chunk.source_file == "01-introduction/01-history.mdx"
        assert chunk.chapter == "01-introduction"
        assert chunk.section == "01-history"
        assert chunk.chunk_index == 0
        assert chunk.token_count == 15
        assert chunk.chunk_type == ChunkType.PARAGRAPH
        assert isinstance(chunk.created_at, datetime)
        assert isinstance(chunk.updated_at, datetime)

    def test_content_chunk_too_short(self):
        """Test ContentChunk validation with content too short."""
        with pytest.raises(ValidationError) as exc_info:
            ContentChunk(
                content="Short",  # Less than 500 chars
                source_file="test.mdx",
                chapter="test",
                section="test",
                chunk_index=0,
                token_count=1,
            )

        assert "min_length" in str(exc_info.value).lower()

    def test_content_chunk_too_long(self):
        """Test ContentChunk validation with content too long."""
        long_content = "x" * 1001  # More than 1000 chars
        with pytest.raises(ValidationError) as exc_info:
            ContentChunk(
                content=long_content,
                source_file="test.mdx",
                chapter="test",
                section="test",
                chunk_index=0,
                token_count=100,
            )

        assert "max_length" in str(exc_info.value).lower()

    def test_content_chunk_negative_token_count(self):
        """Test ContentChunk validation with negative token count."""
        with pytest.raises(ValidationError) as exc_info:
            ContentChunk(
                content="x" * 500,
                source_file="test.mdx",
                chapter="test",
                section="test",
                chunk_index=0,
                token_count=-1,
            )

        assert "greater_than" in str(exc_info.value).lower()

    def test_content_chunk_negative_chunk_index(self):
        """Test ContentChunk validation with negative chunk index."""
        with pytest.raises(ValidationError) as exc_info:
            ContentChunk(
                content="x" * 500,
                source_file="test.mdx",
                chapter="test",
                section="test",
                chunk_index=-1,
                token_count=100,
            )

        assert "greater_than_or_equal" in str(exc_info.value).lower()

    def test_content_chunk_serialization(self):
        """Test ContentChunk JSON serialization."""
        chunk = ContentChunk(
            content="Test content for serialization.",
            source_file="test.mdx",
            chapter="test",
            section="test",
            chunk_index=1,
            token_count=5,
        )

        json_data = chunk.model_dump_json()
        assert "content" in json_data
        assert "source_file" in json_data
        assert "created_at" in json_data
        assert "updated_at" in json_data

    def test_content_chunk_all_chunk_types(self):
        """Test ContentChunk with all valid chunk types."""
        content = "x" * 500

        for chunk_type in ChunkType:
            chunk = ContentChunk(
                content=content,
                source_file="test.mdx",
                chapter="test",
                section="test",
                chunk_index=0,
                token_count=100,
                chunk_type=chunk_type,
            )
            assert chunk.chunk_type == chunk_type

    def test_content_chunk_optional_embedding_id(self):
        """Test ContentChunk with optional embedding_id."""
        chunk = ContentChunk(
            content="x" * 500,
            source_file="test.mdx",
            chapter="test",
            section="test",
            chunk_index=0,
            token_count=100,
            embedding_id="test_embedding_123",
        )

        assert chunk.embedding_id == "test_embedding_123"

        # Test without embedding_id
        chunk_no_embedding = ContentChunk(
            content="x" * 500,
            source_file="test.mdx",
            chapter="test",
            section="test",
            chunk_index=0,
            token_count=100,
        )

        assert chunk_no_embedding.embedding_id is None


class TestChatSession:
    """Test ChatSession model validation and behavior."""

    def test_valid_chat_session_creation(self):
        """Test creating a valid ChatSession."""
        session = ChatSession(
            id="test_session_123",
            ip_address="192.168.1.100",
            user_agent_hash="abc123def456",
        )

        assert session.id == "test_session_123"
        assert session.ip_address == "192.168.1.100"
        assert session.user_agent_hash == "abc123def456"
        assert session.message_count == 0
        assert session.is_active is True
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_activity, datetime)

    def test_chat_session_with_custom_values(self):
        """Test ChatSession with custom values."""
        custom_time = datetime.utcnow() - timedelta(hours=1)
        session = ChatSession(
            id="custom_session",
            ip_address="10.0.0.1",
            user_agent_hash="custom_hash",
            message_count=5,
            is_active=False,
            created_at=custom_time,
            last_activity=custom_time,
        )

        assert session.message_count == 5
        assert session.is_active is False
        assert session.created_at == custom_time
        assert session.last_activity == custom_time

    def test_chat_session_negative_message_count(self):
        """Test ChatSession validation with negative message count."""
        with pytest.raises(ValidationError) as exc_info:
            ChatSession(
                id="test",
                ip_address="127.0.0.1",
                user_agent_hash="hash",
                message_count=-1,
            )

        assert "greater_than_or_equal" in str(exc_info.value).lower()

    def test_chat_session_serialization(self):
        """Test ChatSession JSON serialization."""
        session = ChatSession(
            id="serialization_test",
            ip_address="192.168.1.1",
            user_agent_hash="test_hash",
        )

        json_data = session.model_dump_json()
        assert "id" in json_data
        assert "ip_address" in json_data
        assert "created_at" in json_data
        assert "last_activity" in json_data


class TestQueryLog:
    """Test QueryLog model validation and behavior."""

    def test_valid_query_log_creation(self):
        """Test creating a valid QueryLog."""
        log = QueryLog(
            query_hash="abc123",
            question_length=50,
            response_length=200,
            response_time_ms=1500,
            date_bucket="2025-12-11",
        )

        assert log.query_hash == "abc123"
        assert log.question_length == 50
        assert log.response_length == 200
        assert log.response_time_ms == 1500
        assert log.date_bucket == "2025-12-11"
        assert log.context_provided is False
        assert log.sources_count == 0
        assert isinstance(log.timestamp, datetime)

    def test_query_log_with_context(self):
        """Test QueryLog with context provided."""
        log = QueryLog(
            query_hash="def456",
            question_length=30,
            response_length=150,
            response_time_ms=1200,
            date_bucket="2025-12-11",
            context_provided=True,
            sources_count=3,
        )

        assert log.context_provided is True
        assert log.sources_count == 3

    def test_query_log_invalid_values(self):
        """Test QueryLog validation with invalid values."""
        # Test zero question length
        with pytest.raises(ValidationError):
            QueryLog(
                query_hash="test",
                question_length=0,
                response_length=100,
                response_time_ms=1000,
                date_bucket="2025-12-11",
            )

        # Test negative response length
        with pytest.raises(ValidationError):
            QueryLog(
                query_hash="test",
                question_length=10,
                response_length=-1,
                response_time_ms=1000,
                date_bucket="2025-12-11",
            )

        # Test negative response time
        with pytest.raises(ValidationError):
            QueryLog(
                query_hash="test",
                question_length=10,
                response_length=100,
                response_time_ms=-100,
                date_bucket="2025-12-11",
            )

        # Test negative sources count
        with pytest.raises(ValidationError):
            QueryLog(
                query_hash="test",
                question_length=10,
                response_length=100,
                response_time_ms=1000,
                date_bucket="2025-12-11",
                sources_count=-1,
            )

    def test_query_log_serialization(self):
        """Test QueryLog JSON serialization."""
        log = QueryLog(
            query_hash="serialization_test",
            question_length=25,
            response_length=125,
            response_time_ms=800,
            date_bucket="2025-12-11",
        )

        json_data = log.model_dump_json()
        assert "query_hash" in json_data
        assert "question_length" in json_data
        assert "timestamp" in json_data
        assert "date_bucket" in json_data


class TestChatMessage:
    """Test ChatMessage model validation and behavior."""

    def test_valid_chat_message_creation(self):
        """Test creating a valid ChatMessage."""
        message = ChatMessage(
            session_id="session_123",
            message_type=MessageType.USER,
            content="Hello, how are you?",
        )

        assert message.session_id == "session_123"
        assert message.message_type == MessageType.USER
        assert message.content == "Hello, how are you?"
        assert message.sources is None
        assert message.context_chunks is None
        assert isinstance(message.timestamp, datetime)

    def test_chat_message_with_sources(self):
        """Test ChatMessage with sources."""
        message = ChatMessage(
            session_id="session_456",
            message_type=MessageType.ASSISTANT,
            content="Here is your answer...",
            sources=[
                "01-introduction/01-history.mdx",
                "02-physical-fundamentals/01-kinematics.mdx",
            ],
        )

        assert message.sources == [
            "01-introduction/01-history.mdx",
            "02-physical-fundamentals/01-kinematics.mdx",
        ]

    def test_chat_message_with_context(self):
        """Test ChatMessage with context chunks."""
        message = ChatMessage(
            session_id="session_789",
            message_type=MessageType.USER,
            content="What about this highlighted text?",
            context_chunks=["chunk_1", "chunk_2"],
        )

        assert message.context_chunks == ["chunk_1", "chunk_2"]

    def test_chat_message_all_types(self):
        """Test ChatMessage with all valid message types."""
        for message_type in MessageType:
            message = ChatMessage(
                session_id="test_session",
                message_type=message_type,
                content="Test message",
            )
            assert message.message_type == message_type

    def test_chat_message_serialization(self):
        """Test ChatMessage JSON serialization."""
        message = ChatMessage(
            session_id="serialization_test",
            message_type=MessageType.ASSISTANT,
            content="Test response message",
            sources=["test.mdx"],
        )

        json_data = message.model_dump_json()
        assert "session_id" in json_data
        assert "message_type" in json_data
        assert "content" in json_data
        assert "sources" in json_data
        assert "timestamp" in json_data


class TestEnums:
    """Test enum definitions and behavior."""

    def test_chunk_type_values(self):
        """Test ChunkType enum values."""
        assert ChunkType.PARAGRAPH == "paragraph"
        assert ChunkType.SECTION == "section"
        assert ChunkType.CODE == "code"
        assert ChunkType.LIST == "list"

        # Test iteration
        chunk_types = list(ChunkType)
        assert len(chunk_types) == 4
        assert ChunkType.PARAGRAPH in chunk_types

    def test_message_type_values(self):
        """Test MessageType enum values."""
        assert MessageType.USER == "user"
        assert MessageType.ASSISTANT == "assistant"
        assert MessageType.SYSTEM == "system"

        # Test iteration
        message_types = list(MessageType)
        assert len(message_types) == 3
        assert MessageType.USER in message_types


class TestModelIntegration:
    """Test model integration and relationships."""

    def test_models_with_datetime_consistency(self):
        """Test datetime handling across models."""
        now = datetime.utcnow()

        chunk = ContentChunk(
            content="x" * 500,
            source_file="test.mdx",
            chapter="test",
            section="test",
            chunk_index=0,
            token_count=100,
            created_at=now,
        )

        session = ChatSession(
            id="test", ip_address="127.0.0.1", user_agent_hash="hash", created_at=now
        )

        log = QueryLog(
            query_hash="test",
            question_length=10,
            response_length=100,
            response_time_ms=1000,
            date_bucket="2025-12-11",
            timestamp=now,
        )

        message = ChatMessage(
            session_id="test",
            message_type=MessageType.USER,
            content="test",
            timestamp=now,
        )

        # All should have the same datetime
        assert chunk.created_at == now
        assert session.created_at == now
        assert log.timestamp == now
        assert message.timestamp == now

    def test_model_uuid_generation(self):
        """Test UUID generation for models."""
        chunk1 = ContentChunk(
            content="x" * 500,
            source_file="test1.mdx",
            chapter="test",
            section="test",
            chunk_index=0,
            token_count=100,
        )

        chunk2 = ContentChunk(
            content="y" * 500,
            source_file="test2.mdx",
            chapter="test",
            section="test",
            chunk_index=1,
            token_count=100,
        )

        log1 = QueryLog(
            query_hash="test1",
            question_length=10,
            response_length=100,
            response_time_ms=1000,
            date_bucket="2025-12-11",
        )

        log2 = QueryLog(
            query_hash="test2",
            question_length=20,
            response_length=200,
            response_time_ms=2000,
            date_bucket="2025-12-11",
        )

        message1 = ChatMessage(
            session_id="test", message_type=MessageType.USER, content="test1"
        )

        message2 = ChatMessage(
            session_id="test", message_type=MessageType.ASSISTANT, content="test2"
        )

        # All should have unique IDs
        assert chunk1.id != chunk2.id
        assert log1.id != log2.id
        assert message1.id != message2.id

        # All should be valid UUIDs
        import uuid as uuid_lib

        uuid.UUID(chunk1.id)
        uuid.UUID(chunk2.id)
        uuid.UUID(log1.id)
        uuid.UUID(log2.id)
        uuid.UUID(message1.id)
        uuid.UUID(message2.id)


if __name__ == "__main__":
    pytest.main([__file__])
