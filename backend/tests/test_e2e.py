"""
End-to-end tests for RAG chatbot system.
Tests complete user workflows from frontend to backend.
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

from api.websocket import ConnectionManager, handle_websocket_connection
from services.rag_agent import RAGAgent
from services.query_processor import QueryProcessor
from services.retrieval import RetrievalService


class TestEndToEndWorkflows:
    """Test complete end-to-end user workflows."""

    @pytest.mark.asyncio
    @patch("api.websocket.create_robotics_tutor_agent")
    @patch("api.websocket.manager")
    async def test_complete_qa_workflow(self, mock_agent, mock_manager):
        """Test complete Q&A workflow from question to answer."""
        # Setup mocks
        mock_session_id = "test_session_123"
        mock_manager_instance = Mock()
        mock_manager_instance.connect.return_value = mock_session_id
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        # Mock agent response
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        mock_response = Mock()
        mock_response.choices = [
            Mock(message={"content": "Robotics is the study of robots"})
        ]
        mock_agent_instance.run.return_value = mock_response

        # Mock WebSocket
        mock_websocket = Mock()
        mock_websocket.client = Mock(host="127.0.0.1")
        mock_websocket.headers = {"user-agent": "test-agent"}
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[
                json.dumps(
                    {
                        "type": "question",
                        "data": {"question": "What is robotics?", "context_chunks": []},
                    }
                )
            ]
        )

        # Execute workflow
        await handle_websocket_connection(mock_websocket)

        # Verify connection established
        mock_manager_instance.connect.assert_called_once()
        mock_websocket.accept.assert_called_once()

        # Verify welcome message sent
        welcome_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "welcome"
        ]
        assert len(welcome_calls) == 1

        # Verify agent was called
        mock_agent_instance.run.assert_called_once()

        # Verify response streaming
        response_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] in ["response_start", "response_chunk", "response_end"]
        ]
        assert len(response_calls) >= 3  # start + chunks + end

    @pytest.mark.asyncio
    @patch("api.websocket.create_robotics_tutor_agent")
    @patch("api.websocket.manager")
    async def test_context_aware_workflow(self, mock_agent, mock_manager):
        """Test context-aware workflow with highlighted text."""
        mock_session_id = "test_session_456"
        mock_manager_instance = Mock()
        mock_manager_instance.connect.return_value = mock_session_id
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        # Mock agent response
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message={"content": "Based on the highlighted text about kinematics..."}
            )
        ]
        mock_agent_instance.run.return_value = mock_response

        # Mock WebSocket with context
        mock_websocket = Mock()
        mock_websocket.client = Mock(host="192.168.1.100")
        mock_websocket.headers = {"user-agent": "test-agent"}
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[
                json.dumps(
                    {
                        "type": "question",
                        "data": {
                            "question": "Explain this highlighted text",
                            "context_chunks": ["chunk_1", "chunk_2"],
                        },
                    }
                )
            ]
        )

        # Execute workflow
        await handle_websocket_connection(mock_websocket)

        # Verify context was processed
        mock_agent_instance.run.assert_called_once()
        agent_call_args = mock_agent_instance.run.call_args[0]
        assert "context_chunks" in agent_call_args
        assert agent_call_args["context_chunks"] == ["chunk_1", "chunk_2"]

    @pytest.mark.asyncio
    @patch("api.websocket.create_robotics_tutor_agent")
    @patch("api.websocket.manager")
    async def test_error_handling_workflow(self, mock_agent, mock_manager):
        """Test error handling in workflow."""
        mock_session_id = "test_session_error"
        mock_manager_instance = Mock()
        mock_manager_instance.connect.return_value = mock_session_id
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        # Mock agent to raise error
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        mock_agent_instance.run.side_effect = Exception("Agent processing failed")

        # Mock WebSocket
        mock_websocket = Mock()
        mock_websocket.client = Mock(host="10.0.0.1")
        mock_websocket.headers = {"user-agent": "test-agent"}
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[
                json.dumps(
                    {
                        "type": "question",
                        "data": {
                            "question": "What causes agent error?",
                            "context_chunks": [],
                        },
                    }
                )
            ]
        )

        # Execute workflow
        await handle_websocket_connection(mock_websocket)

        # Verify error response was sent
        error_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "error"
        ]
        assert len(error_calls) >= 1

        error_data = error_calls[0][1]["data"]
        assert error_data["code"] == "SERVICE_UNAVAILABLE"

    @pytest.mark.asyncio
    @patch("api.websocket.create_robotics_tutor_agent")
    @patch("api.websocket.manager")
    async def test_concurrent_users_workflow(self, mock_agent, mock_manager):
        """Test multiple concurrent users."""
        mock_manager_instance = Mock()
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        # Mock agent
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        mock_response = Mock()
        mock_response.choices = [Mock(message={"content": "Response to user"})]
        mock_agent_instance.run.return_value = mock_response

        # Create multiple WebSocket connections
        connections = []
        for i in range(3):
            mock_websocket = Mock()
            mock_websocket.client = Mock(host=f"192.168.1.{i}")
            mock_websocket.headers = {"user-agent": f"test-agent-{i}"}
            mock_websocket.accept = AsyncMock()
            mock_websocket.receive_text = AsyncMock(
                side_effect=[
                    json.dumps(
                        {
                            "type": "question",
                            "data": {
                                "question": f"Question from user {i}",
                                "context_chunks": [],
                            },
                        }
                    )
                ]
            )

            session_id = f"session_{i}"
            mock_manager_instance.connect.return_value = session_id

            # Execute connection
            await handle_websocket_connection(mock_websocket)
            connections.append(session_id)

        # Verify all connections were handled
        assert mock_manager_instance.connect.call_count == 3
        assert len(connections) == 3

        # Verify all users received responses
        response_calls = sum(
            1
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "response_chunk"
        )
        assert response_calls >= 3  # Each user should get response chunks


class TestPerformanceWorkflows:
    """Test performance-related end-to-end scenarios."""

    @pytest.mark.asyncio
    @patch("api.websocket.create_robotics_tutor_agent")
    @patch("api.websocket.manager")
    async def test_response_time_performance(self, mock_agent, mock_manager):
        """Test response time meets performance requirements."""
        import time

        start_time = time.time()

        mock_session_id = "perf_test_session"
        mock_manager_instance = Mock()
        mock_manager_instance.connect.return_value = mock_session_id
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        # Mock agent with realistic response time
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance

        # Create async response generator that simulates streaming
        async def mock_stream():
            # Simulate processing delay
            await asyncio.sleep(0.5)  # 500ms processing
            for i in range(5):
                await asyncio.sleep(0.2)  # 200ms per chunk
                yield f"Response chunk {i}"

        mock_agent_instance.run.return_value = mock_stream()

        # Mock WebSocket
        mock_websocket = Mock()
        mock_websocket.client = Mock(host="127.0.0.1")
        mock_websocket.headers = {"user-agent": "test-agent"}
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[
                json.dumps(
                    {
                        "type": "question",
                        "data": {
                            "question": "Performance test question",
                            "context_chunks": [],
                        },
                    }
                )
            ]
        )

        # Execute workflow
        await handle_websocket_connection(mock_websocket)

        end_time = time.time()
        total_time = end_time - start_time

        # Verify performance requirements
        assert total_time < 2.0  # Should complete in under 2 seconds
        assert total_time > 0.5  # Should take reasonable time

        # Verify response streaming
        response_end_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "response_end"
        ]
        assert len(response_end_calls) == 1

        response_end_data = response_end_calls[0][1]["data"]
        assert response_end_data["response_time_ms"] < 2000

    @pytest.mark.asyncio
    @patch("api.websocket.create_robotics_tutor_agent")
    @patch("api.websocket.manager")
    async def test_memory_usage_under_load(self, mock_agent, mock_manager):
        """Test memory usage under concurrent load."""
        import psutil
        import os

        # Get initial memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        mock_manager_instance = Mock()
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        # Create multiple concurrent connections
        connections = []
        for i in range(10):  # 10 concurrent users
            mock_websocket = Mock()
            mock_websocket.client = Mock(host=f"192.168.1.{i}")
            mock_websocket.accept = AsyncMock()
            mock_websocket.receive_text = AsyncMock(
                side_effect=[
                    json.dumps(
                        {
                            "type": "question",
                            "data": {
                                "question": f"Load test {i}",
                                "context_chunks": [],
                            },
                        }
                    )
                ]
            )

            session_id = f"load_test_{i}"
            mock_manager_instance.connect.return_value = session_id

            # Execute connection
            await handle_websocket_connection(mock_websocket)
            connections.append(session_id)

        # Get peak memory
        peak_memory = process.memory_info().rss

        # Verify memory usage is reasonable
        memory_increase = peak_memory - initial_memory
        memory_increase_mb = memory_increase / (1024 * 1024)

        # Should not use excessive memory (<100MB increase for 10 users)
        assert memory_increase_mb < 100


class TestReliabilityWorkflows:
    """Test reliability and error recovery scenarios."""

    @pytest.mark.asyncio
    @patch("api.websocket.create_robotics_tutor_agent")
    @patch("api.websocket.manager")
    async def test_websocket_reconnection(self, mock_agent, mock_manager):
        """Test WebSocket reconnection handling."""
        mock_manager_instance = Mock()
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        # Mock agent
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        mock_response = Mock()
        mock_response.choices = [Mock(message={"content": "Reconnected response"})]
        mock_agent_instance.run.return_value = mock_response

        # Simulate reconnection scenario
        mock_websocket = Mock()
        mock_websocket.client = Mock(host="127.0.0.1")
        mock_websocket.headers = {"user-agent": "test-agent"}
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[
                json.dumps(
                    {
                        "type": "question",
                        "data": {
                            "question": "After reconnection",
                            "context_chunks": [],
                        },
                    }
                )
            ]
        )

        # First connection
        session_id_1 = await mock_manager_instance.connect(mock_websocket)
        await handle_websocket_connection(mock_websocket)

        # Simulate disconnection and reconnection
        mock_manager_instance.disconnect(session_id_1)

        session_id_2 = await mock_manager_instance.connect(mock_websocket)
        await handle_websocket_connection(mock_websocket)

        # Verify both connections were handled
        assert mock_manager_instance.connect.call_count == 2
        assert mock_manager_instance.disconnect.call_count == 1

        # Verify reconnection got response
        response_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "response_chunk"
        ]
        assert len(response_calls) >= 1

    @pytest.mark.asyncio
    @patch("api.websocket.create_robotics_tutor_agent")
    @patch("api.websocket.manager")
    async def test_external_service_failure_recovery(self, mock_agent, mock_manager):
        """Test recovery from external service failures."""
        mock_manager_instance = Mock()
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        # Mock agent with failure then success
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance

        call_count = 0

        async def failing_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("External service unavailable")
            else:
                mock_response = Mock()
                mock_response.choices = [
                    Mock(message={"content": "Recovered response"})
                ]
                return mock_response

        mock_agent_instance.run.side_effect = failing_run

        # Mock WebSocket
        mock_websocket = Mock()
        mock_websocket.client = Mock(host="127.0.0.1")
        mock_websocket.headers = {"user-agent": "test-agent"}
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[
                json.dumps(
                    {
                        "type": "question",
                        "data": {"question": "Test recovery", "context_chunks": []},
                    }
                ),
                json.dumps(
                    {
                        "type": "question",
                        "data": {
                            "question": "Test recovery again",
                            "context_chunks": [],
                        },
                    }
                ),
            ]
        )

        # First attempt (should fail)
        session_id = await mock_manager_instance.connect(mock_websocket)
        await handle_websocket_connection(mock_websocket)

        # Second attempt (should succeed)
        session_id_2 = await mock_manager_instance.connect(mock_websocket)
        await handle_websocket_connection(mock_websocket)

        # Verify error handling and recovery
        error_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "error"
        ]
        assert len(error_calls) >= 1  # First call should generate error

        success_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "response_chunk"
        ]
        assert len(success_calls) >= 1  # Second call should succeed


class TestSecurityWorkflows:
    """Test security in end-to-end workflows."""

    @pytest.mark.asyncio
    @patch("api.websocket.create_robotics_tutor_agent")
    @patch("api.websocket.manager")
    async def test_input_validation_in_workflow(self, mock_agent, mock_manager):
        """Test input validation in complete workflow."""
        mock_manager_instance = Mock()
        mock_manager_instance.send_message = AsyncMock()
        mock_manager.return_value = mock_manager_instance

        # Mock agent
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance

        # Mock WebSocket with malicious input
        mock_websocket = Mock()
        mock_websocket.client = Mock(host="127.0.0.1")
        mock_websocket.headers = {"user-agent": "test-agent"}
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[
                # Test XSS attempt
                json.dumps(
                    {
                        "type": "question",
                        "data": {
                            "question": "<script>alert('xss')</script>What is robotics?",
                            "context_chunks": [],
                        },
                    }
                ),
                # Test SQL injection attempt
                json.dumps(
                    {
                        "type": "question",
                        "data": {
                            "question": "What is robotics?'; DROP TABLE users; --",
                            "context_chunks": [],
                        },
                    }
                ),
                # Valid question
                json.dumps(
                    {
                        "type": "question",
                        "data": {"question": "What is robotics?", "context_chunks": []},
                    }
                ),
            ]
        )

        # Process malicious inputs (should be rejected)
        for i in range(2):
            session_id = await mock_manager_instance.connect(mock_websocket)
            await handle_websocket_connection(mock_websocket)

        # Process valid input (should succeed)
        session_id = await mock_manager_instance.connect(mock_websocket)
        await handle_websocket_connection(mock_websocket)

        # Verify malicious inputs were rejected
        error_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "error"
        ]
        assert len(error_calls) >= 2  # First two should be rejected

        # Verify valid input was processed
        success_calls = [
            call
            for call in mock_manager_instance.send_message.call_args_list
            if call[1]["type"] == "response_chunk"
        ]
        assert len(success_calls) >= 1  # Last one should succeed


if __name__ == "__main__":
    pytest.main([__file__])
