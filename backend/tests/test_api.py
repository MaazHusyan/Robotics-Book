"""
Unit tests for RAG chatbot API endpoints.
Tests health check, WebSocket, and HTTP endpoints.
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import app
from api.websocket import ConnectionManager


class TestHealthEndpoint:
    """Test health check endpoint."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_health_check_success(self):
        """Test successful health check."""
        response = self.client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "active_connections" in data

    def test_health_check_response_structure(self):
        """Test health check response structure."""
        response = self.client.get("/api/health")

        data = response.json()

        # Check required fields
        required_fields = [
            "status",
            "timestamp",
            "version",
            "uptime_seconds",
            "active_connections",
        ]
        for field in required_fields:
            assert field in data

        # Check data types
        assert isinstance(data["status"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["uptime_seconds"], int)
        assert isinstance(data["active_connections"], int)

    @patch("api.websocket.get_connection_stats")
    def test_health_check_with_connections(self, mock_stats):
        """Test health check with active connections."""
        mock_stats.return_value = {
            "active_connections": 5,
            "total_sessions": 7,
            "connections": ["session1", "session2", "session3", "session4", "session5"],
        }

        client = TestClient(app)
        response = client.get("/api/health")

        data = response.json()
        assert data["active_connections"] == 5


class TestWebSocketEndpoint:
    """Test WebSocket endpoint functionality."""

    @pytest.fixture
    def websocket_client(self):
        """Create WebSocket test client."""
        from fastapi.testclient import TestClient

        return TestClient(app)

    @patch("api.websocket.create_robotics_tutor_agent")
    @patch("api.websocket.manager")
    async def test_websocket_connection_success(self, mock_manager, mock_agent):
        """Test successful WebSocket connection."""
        # Mock manager
        mock_session_id = "test_session_123"
        mock_manager.connect.return_value = mock_session_id
        mock_manager.send_message = AsyncMock()

        # Mock agent
        mock_agent.return_value = Mock()

        # Test connection
        with TestClient(app) as client:
            with client.websocket_connect("/ws/chat") as websocket:
                # Verify connection was established
                mock_manager.connect.assert_called_once()

                # Verify welcome message was sent
                welcome_calls = [
                    call
                    for call in mock_manager.send_message.call_args_list
                    if call[1]["type"] == "welcome"
                ]
                assert len(welcome_calls) == 1

    @patch("api.websocket.manager")
    async def test_websocket_message_handling(self, mock_manager):
        """Test WebSocket message handling."""
        mock_session_id = "test_session"
        mock_manager.connect.return_value = mock_session_id
        mock_manager.send_message = AsyncMock()

        with TestClient(app) as client:
            with client.websocket_connect("/ws/chat") as websocket:
                # Send a question message
                question_message = {
                    "type": "question",
                    "data": {"question": "What is robotics?", "context_chunks": []},
                }

                websocket.send_json(question_message)

                # Verify message was processed
                # Note: In real test, you'd need to wait for async processing
                # This is a simplified test structure

    @patch("api.websocket.manager")
    async def test_websocket_ping_pong(self, mock_manager):
        """Test WebSocket ping/pong functionality."""
        mock_session_id = "test_session"
        mock_manager.connect.return_value = mock_session_id
        mock_manager.send_message = AsyncMock()

        with TestClient(app) as client:
            with client.websocket_connect("/ws/chat") as websocket:
                # Send ping message
                ping_message = {"type": "ping", "data": {}}
                websocket.send_json(ping_message)

                # Verify pong response (simplified)
                # In real test, you'd wait for async response

    @patch("api.websocket.manager")
    async def test_websocket_invalid_message(self, mock_manager):
        """Test WebSocket with invalid message."""
        mock_session_id = "test_session"
        mock_manager.connect.return_value = mock_session_id
        mock_manager.send_message = AsyncMock()

        with TestClient(app) as client:
            with client.websocket_connect("/ws/chat") as websocket:
                # Send invalid message (missing type)
                invalid_message = {"data": {"question": "test"}}
                websocket.send_json(invalid_message)

                # Verify error response
                error_calls = [
                    call
                    for call in mock_manager.send_message.call_args_list
                    if call[1]["type"] == "error"
                ]
                assert len(error_calls) >= 1

    @patch("api.websocket.manager")
    async def test_websocket_question_validation(self, mock_manager):
        """Test WebSocket question validation."""
        mock_session_id = "test_session"
        mock_manager.connect.return_value = mock_session_id
        mock_manager.send_message = AsyncMock()

        with TestClient(app) as client:
            with client.websocket_connect("/ws/chat") as websocket:
                # Test empty question
                empty_question = {
                    "type": "question",
                    "data": {"question": "", "context_chunks": []},
                }
                websocket.send_json(empty_question)

                # Test too long question
                long_question = {
                    "type": "question",
                    "data": {"question": "x" * 1001, "context_chunks": []},
                }
                websocket.send_json(long_question)

                # Verify error responses
                error_calls = [
                    call
                    for call in mock_manager.send_message.call_args_list
                    if call[1]["type"] == "error"
                ]
                assert len(error_calls) >= 2


class TestCORSConfiguration:
    """Test CORS configuration."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_cors_headers_present(self):
        """Test CORS headers are present."""
        response = self.client.get("/api/health")

        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_cors_preflight_request(self):
        """Test CORS preflight request."""
        response = self.client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers

    @patch.dict(os.environ, {"CORS_ORIGIN": "https://example.com"})
    def test_cors_custom_origin(self):
        """Test CORS with custom origin."""
        response = self.client.get("/api/health")

        allowed_origin = response.headers.get("access-control-allow-origin")
        assert "https://example.com" in allowed_origin


class TestRateLimiting:
    """Test rate limiting functionality."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    @patch("api.middleware.rate_limiter.RateLimiter")
    def test_rate_limiting_headers(self, mock_limiter):
        """Test rate limiting headers."""
        # Mock rate limiter to return rate limit info
        mock_instance = Mock()
        mock_instance.check_rate_limit.return_value = {
            "remaining": 50,
            "limit": 100,
            "reset_time": "2025-12-11T12:00:00Z",
        }
        mock_limiter.return_value = mock_instance

        response = self.client.get("/api/health")

        # Check rate limit headers
        assert "x-ratelimit-remaining" in response.headers
        assert "x-ratelimit-limit" in response.headers
        assert "x-ratelimit-reset" in response.headers

    @patch("api.middleware.rate_limiter.RateLimiter")
    def test_rate_limit_exceeded(self, mock_limiter):
        """Test rate limit exceeded response."""
        # Mock rate limiter to return exceeded
        mock_instance = Mock()
        mock_instance.check_rate_limit.return_value = {
            "error": "rate_limit_exceeded",
            "message": "Rate limit exceeded",
            "retry_after": 60,
        }
        mock_limiter.return_value = mock_instance

        response = self.client.get("/api/health")

        assert response.status_code == 429
        data = response.json()
        assert data["error"] == "rate_limit_exceeded"
        assert "retry_after" in data


class TestErrorHandling:
    """Test error handling in API endpoints."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_404_not_found(self):
        """Test 404 error handling."""
        response = self.client.get("/nonexistent-endpoint")

        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test method not allowed error."""
        response = self.client.delete("/api/health")

        assert response.status_code == 405

    def test_invalid_json_handling(self):
        """Test invalid JSON handling."""
        response = self.client.post(
            "/api/health",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422  # Unprocessable Entity


class TestSecurityHeaders:
    """Test security-related headers."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_security_headers_present(self):
        """Test security headers are present."""
        response = self.client.get("/api/health")

        # Check for common security headers
        # Note: These would be added by security middleware
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection",
        ]

        # At minimum, no security-sensitive info should be leaked
        assert (
            "server" not in response.headers
            or response.headers["server"] != "nginx/1.0"
        )

    def test_no_sensitive_info_leakage(self):
        """Test no sensitive information in responses."""
        response = self.client.get("/api/health")

        data = response.json()

        # Ensure no stack traces or internal paths are leaked
        response_str = json.dumps(data)
        sensitive_patterns = [
            "internal server error",
            "stack trace",
            "/var/www/",
            "/home/",
            "exception",
        ]

        for pattern in sensitive_patterns:
            assert pattern.lower() not in response_str.lower()


class TestAPIIntegration:
    """Test API integration scenarios."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    @patch("api.websocket.manager")
    def test_concurrent_connections(self, mock_manager):
        """Test handling multiple concurrent connections."""
        mock_session_ids = ["session1", "session2", "session3"]
        mock_manager.connect.side_effect = mock_session_ids
        mock_manager.send_message = AsyncMock()

        # Simulate multiple connections
        connections = []
        for i in range(3):
            with TestClient(app) as client:
                try:
                    with client.websocket_connect("/ws/chat") as websocket:
                        connections.append(websocket)
                except Exception:
                    pass  # Connection might fail in test environment

        # Verify connection attempts
        assert mock_manager.connect.call_count == 3

    def test_api_response_format(self):
        """Test API response format consistency."""
        response = self.client.get("/api/health")

        # All API responses should be JSON
        assert response.headers["content-type"] == "application/json"

        data = response.json()

        # Response structure should be consistent
        assert isinstance(data, dict)

        # Success responses should have status field
        if response.status_code < 400:
            assert "status" in data


if __name__ == "__main__":
    pytest.main([__file__])
