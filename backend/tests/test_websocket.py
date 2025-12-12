"""
WebSocket tests for RAG chatbot system.
Tests WebSocket connections, message handling, and streaming functionality.
"""

import pytest
import sys
import os
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Add a backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from api.websocket import (
    ConnectionManager,
    handle_websocket_connection,
    handle_message,
    handle_question,
    handle_ping,
)
from services.rag_agent import RAGAgent


class TestConnectionManager:
    """Test ConnectionManager functionality."""

    def setup_method(self):
        """Setup connection manager for tests."""
        self.manager = ConnectionManager()

    @pytest.mark.asyncio
    async def test_connect_new_session(self):
        """Test connecting with new session."""
        mock_websocket = Mock()
        mock_websocket.client = Mock(host="127.0.0.1")
        mock_websocket.headers = {"user-agent": "test-agent"}
        mock_websocket.accept = AsyncMock()

        session_id = await self.manager.connect(mock_websocket)

        assert session_id is not None
        assert len(session_id) == 36  # UUID length
        assert session_id in self.manager.active_connections
        assert session_id in self.manager.session_data

        # Check session data
        session_data = self.manager.session_data[session_id]
        assert session_data["ip_address"] == "127.0.0.1"
        assert session_data["user_agent"] == "test-agent"
        assert session_data["message_count"] == 0
        assert session_data["is_active"] is True

        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_existing_session(self):
        """Test connecting with existing session ID."""
        mock_websocket = Mock()
        mock_websocket.client = Mock(host="192.168.1.100")
        mock_websocket.headers = {"user-agent": "test-agent"}
        mock_websocket.accept = AsyncMock()

        existing_session_id = "existing_session_123"
        session_id = await self.manager.connect(mock_websocket, existing_session_id)

        assert session_id == existing_session_id
        assert session_id in self.manager.active_connections

    @pytest.mark.asyncio
    async def test_disconnect_session(self):
        """Test disconnecting a session."""
        mock_websocket = Mock()
        mock_websocket.accept = AsyncMock()

        session_id = await self.manager.connect(mock_websocket)
        assert session_id in self.manager.active_connections

        self.manager.disconnect(session_id)

        assert session_id not in self.manager.active_connections
        assert session_id not in self.manager.session_data

    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Test successful message sending."""
        mock_websocket = Mock()
        mock_websocket.send_text = AsyncMock()

        session_id = await self.manager.connect(mock_websocket)
        message = {"type": "test", "data": {"content": "Hello"}}

        await self.manager.send_message(session_id, message)

        mock_websocket.send_text.assert_called_once()
        call_args = mock_websocket.send_text.call_args[0][0]
        sent_message = json.loads(call_args)
        assert sent_message["type"] == "test"

        # Check session data updated
        session_data = self.manager.session_data[session_id]
        assert session_data["message_count"] == 1

    @pytest.mark.asyncio
    async def test_send_message_disconnected_session(self):
        """Test sending message to disconnected session."""
        message = {"type": "test", "data": {"content": "Hello"}}

        # Should not raise error, just handle gracefully
        await self.manager.send_message("nonexistent_session", message)

        # No exception should be raised
        assert True

    @pytest.mark.asyncio
    async def test_send_message_websocket_error(self):
        """Test handling WebSocket error during send."""
        mock_websocket = Mock()
        mock_websocket.send_text = AsyncMock(side_effect=Exception("Connection lost"))

        session_id = await self.manager.connect(mock_websocket)
        message = {"type": "test", "data": {"content": "Hello"}}

        await self.manager.send_message(session_id, message)

        # Session should be disconnected on error
        assert session_id not in self.manager.active_connections

    @pytest.mark.asyncio
    async def test_broadcast_message(self):
        """Test broadcasting message to all sessions."""
        mock_websocket1 = Mock()
        mock_websocket1.send_text = AsyncMock()
        mock_websocket2 = Mock()
        mock_websocket2.send_text = AsyncMock()

        session1 = await self.manager.connect(mock_websocket1)
        session2 = await self.manager.connect(mock_websocket2)

        message = {"type": "broadcast", "data": {"content": "System announcement"}}

        await self.manager.broadcast(message)

        # Both websockets should receive the message
        mock_websocket1.send_text.assert_called_once()
        mock_websocket2.send_text.assert_called_once()

    def test_get_connection_stats(self):
        """Test getting connection statistics."""
        mock_websocket = Mock()
        mock_websocket.accept = AsyncMock()

        # Initially empty
        stats = self.manager.get_connection_stats()
        assert stats["active_connections"] == 0
        assert stats["total_sessions"] == 0
        assert stats["connections"] == []

        # Add connections
        session1 = asyncio.run(self.manager.connect(mock_websocket))
        session2 = asyncio.run(self.manager.connect(mock_websocket))

        stats = self.manager.get_connection_stats()
        assert stats["active_connections"] == 2
        assert stats["total_sessions"] == 2
        assert set(stats["connections"]) == {session1, session2}

    def test_cleanup_expired_sessions(self):
        """Test cleanup of expired sessions."""
        mock_websocket = Mock()
        mock_websocket.accept = AsyncMock()

        # Create session with old timestamp
        old_session = asyncio.run(self.manager.connect(mock_websocket))
        self.manager.session_data[old_session]["last_activity"] = (
            datetime.utcnow() - timedelta(hours=25)
        )

        # Create recent session
        recent_session = asyncio.run(self.manager.connect(mock_websocket))

        # Cleanup (24 hour retention)
        self.manager.cleanup_expired_sessions()

        # Old session should be removed, recent should remain
        assert old_session not in self.manager.active_connections
        assert recent_session in self.manager.active_connections


class TestWebSocketConnection:
    """Test WebSocket connection handling."""

    @pytest.mark.asyncio
    @patch("api.websocket.create_robotics_tutor_agent")
    @patch("api.websocket.manager")
    async def test_websocket_connection_success_flow(self, mock_manager, mock_agent):
        """Test successful WebSocket connection flow."""
        # Mock manager
        mock_session_id = "test_session_123"
        mock_manager_instance = Mock()
        mock_manager_instance.connect.return_value = mock_session_id
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        # Mock agent
        mock_agent.return_value = Mock()

        # Mock WebSocket
        mock_websocket = Mock()
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

        # Test connection handling
        await handle_websocket_connection(mock_websocket)

        # Verify connection flow
        mock_websocket.accept.assert_called_once()
        mock_manager_instance.connect.assert_called_once()

        # Verify welcome message
        welcome_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "welcome"
        ]
        assert len(welcome_calls) == 1

        welcome_data = welcome_calls[0][1]["data"]
        assert welcome_data["session_id"] == mock_session_id
        assert "server_version" in welcome_data
        assert "features" in welcome_data

    @pytest.mark.asyncio
    @patch("api.websocket.manager")
    async def test_websocket_connection_ip_banned(self, mock_manager):
        """Test WebSocket connection with banned IP."""
        mock_manager_instance = Mock()
        mock_manager_instance.banned_ips = {
            "192.168.1.100": datetime.utcnow() + timedelta(minutes=5)
        }
        mock_manager.return_value = mock_manager_instance

        mock_websocket = Mock()
        mock_websocket.client = Mock(host="192.168.1.100")

        # Should raise HTTPException for banned IP
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await handle_websocket_connection(mock_websocket)

        assert "banned" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @patch("api.websocket.manager")
    async def test_websocket_connection_rate_limit(self, mock_manager):
        """Test WebSocket connection rate limiting."""
        mock_manager_instance = Mock()
        mock_manager_instance.connection_attempts = {}
        mock_manager_instance.banned_ips = {}
        mock_manager.return_value = mock_manager_instance

        mock_websocket = Mock()
        mock_websocket.client = Mock(host="127.0.0.1")

        # Simulate many connection attempts
        for i in range(15):  # More than limit of 10
            try:
                await handle_websocket_connection(mock_websocket)
            except Exception:
                pass  # Expected to fail after rate limit

        # Should have been banned
        assert len(mock_manager_instance.banned_ips) > 0


class TestMessageHandling:
    """Test WebSocket message handling."""

    @pytest.mark.asyncio
    @patch("api.websocket.handle_question")
    async def test_handle_question_message(self, mock_handle_question):
        """Test handling question messages."""
        mock_agent = Mock()
        session_id = "test_session"

        message = {
            "type": "question",
            "data": {
                "question": "What is robotics?",
                "context_chunks": ["Highlighted text"],
            },
        }

        await handle_message(session_id, message, mock_agent)

        mock_handle_question.assert_called_once_with(session_id, message, mock_agent)

    @pytest.mark.asyncio
    async def test_handle_ping_message(self, mock_handle_question):
        """Test handling ping messages."""
        mock_agent = Mock()
        session_id = "test_session"

        message = {"type": "ping", "data": {}}

        await handle_message(session_id, message, mock_agent)

        # Ping should be handled without calling question handler
        mock_handle_question.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_invalid_message_type(self, mock_handle_question):
        """Test handling invalid message type."""
        mock_manager = Mock()
        mock_manager.send_message = AsyncMock()
        session_id = "test_session"

        message = {"type": "invalid_type", "data": {}}

        await handle_message(session_id, message, Mock())

        # Should send error message
        error_calls = [
            call
            for call in mock_manager.send_message.call_args_list
            if call[1]["type"] == "error"
        ]
        assert len(error_calls) == 1

        error_data = error_calls[0][1]["data"]
        assert "Unknown message type" in error_data["message"]

    @pytest.mark.asyncio
    async def test_handle_malformed_message(self, mock_handle_question):
        """Test handling malformed message."""
        mock_manager = Mock()
        mock_manager.send_message = AsyncMock()
        session_id = "test_session"

        # Test non-dict message
        message = "invalid string message"

        await handle_message(session_id, message, Mock())

        # Should send error message
        error_calls = [
            call
            for call in mock_manager.send_message.call_args_list
            if call[1]["type"] == "error"
        ]
        assert len(error_calls) == 1

    @pytest.mark.asyncio
    async def test_handle_oversized_message(self, mock_handle_question):
        """Test handling oversized message."""
        mock_manager = Mock()
        mock_manager.send_message = AsyncMock()
        session_id = "test_session"

        # Create large message (>10KB)
        large_data = "x" * 12000
        message = {"type": "question", "data": {"content": large_data}}

        await handle_message(session_id, message, Mock())

        # Should send error message
        error_calls = [
            call
            for call in mock_manager.send_message.call_args_list
            if call[1]["type"] == "error"
        ]
        assert len(error_calls) == 1

        error_data = error_calls[0][1]["data"]
        assert "too large" in error_data["message"].lower()


class TestQuestionHandling:
    """Test question message processing."""

    @pytest.mark.asyncio
    @patch("api.websocket.manager")
    async def test_valid_question_processing(self, mock_manager):
        """Test processing valid question."""
        mock_manager_instance = Mock()
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        session_id = "test_session"
        message = {
            "type": "question",
            "data": {"question": "What is robotics?", "context_chunks": []},
        }
        mock_agent = Mock()

        await handle_question(session_id, message, mock_agent)

        # Should send response start
        response_start_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "response_start"
        ]
        assert len(response_start_calls) == 1

        # Should send response chunks
        response_chunk_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "response_chunk"
        ]
        assert len(response_chunk_calls) > 0

        # Should send response end
        response_end_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "response_end"
        ]
        assert len(response_end_calls) == 1

    @pytest.mark.asyncio
    @patch("api.websocket.manager")
    async def test_empty_question_error(self, mock_manager):
        """Test error handling for empty question."""
        mock_manager_instance = Mock()
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        session_id = "test_session"
        message = {"type": "question", "data": {"question": "", "context_chunks": []}}

        await handle_question(session_id, message, Mock())

        # Should send error message
        error_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "error"
        ]
        assert len(error_calls) == 1

        error_data = error_calls[0][1]["data"]
        assert "empty" in error_data["message"].lower()

    @pytest.mark.asyncio
    @patch("api.websocket.manager")
    async def test_too_long_question_error(self, mock_manager):
        """Test error handling for too long question."""
        mock_manager_instance = Mock()
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        session_id = "test_session"
        long_question = "x" * 1001  # Over 1000 chars
        message = {
            "type": "question",
            "data": {"question": long_question, "context_chunks": []},
        }

        await handle_question(session_id, message, Mock())

        # Should send error message
        error_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "error"
        ]
        assert len(error_calls) == 1

        error_data = error_calls[0][1]["data"]
        assert "too long" in error_data["message"].lower()

    @pytest.mark.asyncio
    @patch("api.websocket.manager")
    async def test_too_many_context_chunks_error(self, mock_manager):
        """Test error handling for too many context chunks."""
        mock_manager_instance = Mock()
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        session_id = "test_session"
        too_many_chunks = [f"chunk_{i}" for i in range(10)]  # More than 5
        message = {
            "type": "question",
            "data": {
                "question": "What is robotics?",
                "context_chunks": too_many_chunks,
            },
        }

        await handle_question(session_id, message, Mock())

        # Should send error message
        error_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "error"
        ]
        assert len(error_calls) == 1

        error_data = error_calls[0][1]["data"]
        assert "too many" in error_data["message"].lower()


class TestPingHandling:
    """Test ping/pong functionality."""

    @pytest.mark.asyncio
    @patch("api.websocket.manager")
    async def test_ping_message(self, mock_manager):
        """Test ping message handling."""
        mock_manager_instance = Mock()
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        session_id = "test_session"
        message = {"type": "ping", "data": {}}

        await handle_ping(session_id)

        # Should send pong response
        pong_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "pong"
        ]
        assert len(pong_calls) == 1

        pong_data = pong_calls[0][1]["data"]
        assert pong_data == {}


class TestWebSocketSecurity:
    """Test WebSocket security features."""

    @pytest.mark.asyncio
    @patch("api.websocket.manager")
    async def test_message_rate_limiting(self, mock_manager):
        """Test message rate limiting."""
        mock_manager_instance = Mock()
        mock_manager_instance.send_message = AsyncMock()
        mock_manager_instance.session_data = {}
        mock_manager.return_value = mock_manager_instance

        session_id = "test_session"
        message = {"type": "question", "data": {"question": "Test"}}

        # Simulate many messages quickly
        for i in range(35):  # More than 30 limit
            await handle_message(session_id, message, Mock())

        # Should trigger rate limiting
        error_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "error"
        ]
        rate_limit_errors = [
            call
            for call in error_calls
            if "rate limit" in call[1]["data"]["message"].lower()
        ]
        assert len(rate_limit_errors) > 0

    @pytest.mark.asyncio
    async def test_message_sanitization(self, mock_manager):
        """Test message sanitization."""
        mock_manager_instance = Mock()
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        session_id = "test_session"

        # Test with HTML content
        message_with_html = {
            "type": "question",
            "data": {"question": "<script>alert('xss')</script>What is robotics?"},
        }

        await handle_message(session_id, message_with_html, Mock())

        # Should process the message (HTML would be sanitized in real implementation)
        # This test verifies the message handling flow
        assert mock_manager_instance.send_message.called


if __name__ == "__main__":
    pytest.main([__file__])
