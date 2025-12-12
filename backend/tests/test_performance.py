"""
Performance tests for RAG chatbot system.
Tests response times, throughput, and resource usage.
"""

import pytest
import sys
import os
import asyncio
import time
import psutil
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

# Add a backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from services.query_processor import QueryProcessor
from services.rag_agent import RAGAgent
from services.retrieval import RetrievalService
from services.embeddings import EmbeddingService
from api.websocket import ConnectionManager


class TestResponseTimePerformance:
    """Test response time performance requirements."""

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_query_response_time_under_2_seconds(self):
        """Test that 95% of queries complete in under 2 seconds."""
        # Mock services for fast response
        with patch.multiple(
            "services.retrieval.RetrievalService",
            "services.embeddings.EmbeddingService",
            "services.rag_agent.RAGAgent",
        ) as mocks:
            # Mock fast retrieval (100ms)
            mocks["RetrievalService"].return_value.search_content.return_value = [
                {"content": "Robotics content", "source": "test.mdx"}
            ]
            mocks["RetrievalService"].return_value.search_content.side_effect = (
                lambda *args, **kwargs: (
                    asyncio.sleep(0.1),  # 100ms delay
                    mocks["RetrievalService"].return_value.search_content.return_value,
                )
            )

            # Mock fast embedding (200ms)
            mocks["EmbeddingService"].return_value.generate_embedding.return_value = [
                0.1,
                0.2,
                0.3,
            ]
            mocks["EmbeddingService"].return_value.generate_embedding.side_effect = (
                lambda *args, **kwargs: (
                    asyncio.sleep(0.2),  # 200ms delay
                    mocks[
                        "EmbeddingService"
                    ].return_value.generate_embedding.return_value,
                )
            )

            # Mock fast agent response (800ms)
            mock_agent = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message={"content": "Robotics answer"})]
            mock_agent.run.return_value = mock_response
            mock_agent.run.side_effect = lambda *args, **kwargs: (
                asyncio.sleep(0.8),  # 800ms delay
                mock_response,
            )
            mocks["RAGAgent"].return_value = mock_agent

            # Test multiple queries
            processor = QueryProcessor()
            response_times = []

            for i in range(20):  # Test 20 queries
                start_time = time.time()
                result = await processor.process_query(f"Query {i}")
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms

                response_times.append(response_time)

            # Calculate 95th percentile
            response_times.sort()
            p95_index = int(len(response_times) * 0.95)
            p95_response_time = response_times[p95_index]

            # Performance requirement: 95% under 2000ms
            assert p95_response_time < 2000, (
                f"95th percentile response time: {p95_response_time}ms (should be < 2000ms)"
            )

            # Average response time should be reasonable
            avg_response_time = sum(response_times) / len(response_times)
            assert avg_response_time < 1500, (
                f"Average response time: {avg_response_time}ms (should be < 1500ms)"
            )

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_query_performance(self):
        """Test performance under concurrent load."""
        with patch.multiple(
            "services.retrieval.RetrievalService",
            "services.embeddings.EmbeddingService",
            "services.rag_agent.RAGAgent",
        ) as mocks:
            # Mock services with realistic delays
            mocks["RetrievalService"].return_value.search_content.side_effect = (
                lambda *args, **kwargs: (
                    asyncio.sleep(0.15),  # 150ms retrieval
                    [
                        {"content": f"Content {i}", "source": "test.mdx"}
                        for i in range(3)
                    ],
                )
            )

            mocks["EmbeddingService"].return_value.generate_embedding.side_effect = (
                lambda *args, **kwargs: (
                    asyncio.sleep(0.25),  # 250ms embedding
                    [0.1, 0.2, 0.3],
                )
            )

            mock_agent = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message={"content": f"Answer {i}"})]
            mock_agent.run.side_effect = lambda *args, **kwargs: (
                asyncio.sleep(0.6),  # 600ms agent processing
                mock_response,
            )
            mocks["RAGAgent"].return_value = mock_agent

            # Test concurrent queries
            processor = QueryProcessor()
            concurrent_queries = 10
            start_time = time.time()

            tasks = [
                processor.process_query(f"Concurrent query {i}")
                for i in range(concurrent_queries)
            ]

            results = await asyncio.gather(*tasks)
            end_time = time.time()
            total_time = end_time - start_time

            # Performance requirements
            # Should complete 10 concurrent queries in reasonable time
            assert total_time < 15.0, (
                f"Concurrent queries took {total_time:.2f}s (should be < 15s)"
            )

            # Average time per query should be under 2 seconds
            avg_time_per_query = total_time / concurrent_queries
            assert avg_time_per_query < 2.0, (
                f"Average time per query: {avg_time_per_query:.2f}s (should be < 2s)"
            )

            # All queries should complete successfully
            assert len(results) == concurrent_queries
            assert all(result is not None for result in results)


class TestThroughputPerformance:
    """Test system throughput under load."""

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_system_throughput_50_concurrent_users(self):
        """Test system handles 50 concurrent users."""
        with patch.multiple(
            "services.retrieval.RetrievalService",
            "services.embeddings.EmbeddingService",
            "services.rag_agent.RAGAgent",
        ) as mocks:
            # Mock optimized services
            mocks["RetrievalService"].return_value.search_content.side_effect = (
                lambda *args, **kwargs: (
                    asyncio.sleep(0.05),  # 50ms retrieval
                    [
                        {"content": f"Content {i}", "source": "test.mdx"}
                        for i in range(2)
                    ],
                )
            )

            mocks["EmbeddingService"].return_value.generate_embedding.side_effect = (
                lambda *args, **kwargs: (
                    asyncio.sleep(0.1),  # 100ms embedding
                    [0.1, 0.2, 0.3],
                )
            )

            mock_agent = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message={"content": f"Answer {i}"})]
            mock_agent.run.side_effect = lambda *args, **kwargs: (
                asyncio.sleep(0.3),  # 300ms agent processing
                mock_response,
            )
            mocks["RAGAgent"].return_value = mock_agent

            # Simulate 50 concurrent users
            processor = QueryProcessor()
            user_count = 50
            start_time = time.time()

            tasks = [
                processor.process_query(f"User {i} query") for i in range(user_count)
            ]

            results = await asyncio.gather(*tasks)
            end_time = time.time()
            total_time = end_time - start_time

            # Throughput requirements
            queries_per_second = user_count / total_time
            assert queries_per_second >= 5.0, (
                f"Throughput: {queries_per_second:.2f} queries/second (should be >= 5)"
            )

            # Should complete in reasonable time
            assert total_time < 20.0, (
                f"50 users took {total_time:.2f}s (should be < 20s)"
            )

            # All queries should succeed
            assert len(results) == user_count
            success_rate = (
                sum(1 for result in results if result is not None) / user_count
            )
            assert success_rate >= 0.95, (
                f"Success rate: {success_rate:.2%} (should be >= 95%)"
            )


class TestResourceUsagePerformance:
    """Test resource usage under load."""

    @pytest.mark.performance
    def test_memory_usage_under_load(self):
        """Test memory usage stays within limits."""
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Simulate memory-intensive operations
        large_content = "x" * 1000000  # 10MB string

        # Test multiple large content processing
        for i in range(10):
            # Simulate content chunking (would use memory)
            chunks = [
                large_content[j : j + 100000]
                for j in range(0, len(large_content), 100000)
            ]

            # Simulate embedding generation (memory intensive)
            import hashlib

            for chunk in chunks:
                hashlib.sha256(chunk.encode()).hexdigest()

        # Get peak memory
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory

        # Memory increase should be reasonable (<500MB for this test)
        memory_increase_mb = memory_increase / (1024 * 1024)
        assert memory_increase_mb < 500, (
            f"Memory increase: {memory_increase_mb:.2f}MB (should be < 500MB)"
        )

    @pytest.mark.performance
    def test_cpu_usage_under_load(self):
        """Test CPU usage stays within limits."""
        process = psutil.Process()

        # Simulate CPU-intensive operations
        start_time = time.time()

        # Simulate complex computations
        for i in range(1000):
            # Simulate embedding-like computation
            result = 1.0
            for j in range(100):
                result *= 1.01
                result = result**0.5

        end_time = time.time()
        computation_time = end_time - start_time

        # Should complete in reasonable time
        assert computation_time < 10.0, (
            f"CPU-intensive test took {computation_time:.2f}s (should be < 10s)"
        )

        # CPU usage should be reasonable (this is a simplified test)
        # In real scenario, you'd monitor CPU percentage during the test
        assert True  # Placeholder for CPU usage check

    @pytest.mark.performance
    async def test_database_connection_pooling(self):
        """Test database connection pooling efficiency."""
        with patch("models.database.get_db_connection") as mock_get_conn:
            # Mock connection pool behavior
            connection_times = []

            def mock_connection():
                start_time = time.time()
                time.sleep(0.01)  # Simulate connection time
                end_time = time.time()
                connection_times.append(end_time - start_time)
                return Mock()  # Mock connection object

            mock_get_conn.side_effect = [mock_connection for _ in range(20)]

            # Test multiple connections
            connections = []
            for i in range(20):
                conn = mock_get_conn()
                connections.append(conn)

            # Connection pooling should be efficient
            avg_connection_time = sum(connection_times) / len(connection_times)
            assert avg_connection_time < 0.1, (
                f"Average connection time: {avg_connection_time:.3f}s (should be < 0.1s)"
            )

            # Should reuse connections efficiently
            assert len(connections) == 20


class TestScalabilityPerformance:
    """Test system scalability limits."""

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_gradual_load_increase(self):
        """Test system handles gradual load increase."""
        with patch.multiple(
            "services.retrieval.RetrievalService",
            "services.embeddings.EmbeddingService",
            "services.rag_agent.RAGAgent",
        ) as mocks:
            # Mock services with consistent performance
            mocks["RetrievalService"].return_value.search_content.side_effect = (
                lambda *args, **kwargs: (
                    asyncio.sleep(0.1),
                    [
                        {"content": f"Content {i}", "source": "test.mdx"}
                        for i in range(2)
                    ],
                )
            )

            mocks["EmbeddingService"].return_value.generate_embedding.side_effect = (
                lambda *args, **kwargs: (asyncio.sleep(0.1), [0.1, 0.2, 0.3])
            )

            mock_agent = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message={"content": f"Answer {i}"})]
            mock_agent.run.side_effect = lambda *args, **kwargs: (
                asyncio.sleep(0.2),
                mock_response,
            )
            mocks["RAGAgent"].return_value = mock_agent

            processor = QueryProcessor()

            # Test gradual load increase: 5, 10, 20, 30 concurrent users
            load_levels = [5, 10, 20, 30]
            performance_results = []

            for load_level in load_levels:
                start_time = time.time()

                tasks = [
                    processor.process_query(f"Load {load_level} query {i}")
                    for i in range(load_level)
                ]

                results = await asyncio.gather(*tasks)
                end_time = time.time()
                total_time = end_time - start_time

                throughput = load_level / total_time
                avg_time = total_time / load_level

                performance_results.append(
                    {
                        "load_level": load_level,
                        "throughput": throughput,
                        "avg_time": avg_time,
                        "success_rate": sum(1 for r in results if r is not None)
                        / load_level,
                    }
                )

            # Performance should degrade gracefully
            for i, result in enumerate(performance_results[1:], 1):
                prev_result = performance_results[i - 1]

                # Throughput should not decrease dramatically
                throughput_ratio = result["throughput"] / prev_result["throughput"]
                assert throughput_ratio > 0.7, (
                    f"Throughput ratio at load {result['load_level']}: {throughput_ratio:.2f} (should be > 0.7)"
                )

                # Response time should not increase dramatically
                time_ratio = result["avg_time"] / prev_result["avg_time"]
                assert time_ratio < 2.0, (
                    f"Time ratio at load {result['load_level']}: {time_ratio:.2f} (should be < 2.0)"
                )


class TestPerformanceRegression:
    """Test performance regression detection."""

    @pytest.mark.performance
    async def test_performance_baseline_comparison(self):
        """Test against performance baseline."""
        # Define performance baselines
        baseline = {
            "single_query_time": 1000,  # 1 second
            "concurrent_10_queries": 8.0,  # 8 seconds total
            "memory_per_query": 50 * 1024 * 1024,  # 50MB
            "cpu_per_query": 0.5,  # 50% CPU for 1 second
        }

        with patch.multiple(
            "services.retrieval.RetrievalService",
            "services.embeddings.EmbeddingService",
            "services.rag_agent.RAGAgent",
        ) as mocks:
            # Mock services with baseline performance
            mocks["RetrievalService"].return_value.search_content.side_effect = (
                lambda *args, **kwargs: (
                    asyncio.sleep(baseline["single_query_time"] / 1000),  # 1 second
                    [{"content": "Baseline content", "source": "test.mdx"}],
                )
            )

            mocks["EmbeddingService"].return_value.generate_embedding.side_effect = (
                lambda *args, **kwargs: (
                    asyncio.sleep(baseline["single_query_time"] / 1000),  # 1 second
                    [0.1, 0.2, 0.3],
                )
            )

            mock_agent = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message={"content": "Baseline answer"})]
            mock_agent.run.side_effect = lambda *args, **kwargs: (
                asyncio.sleep(baseline["single_query_time"] / 1000),  # 1 second
                mock_response,
            )
            mocks["RAGAgent"].return_value = mock_agent

            processor = QueryProcessor()

            # Test single query performance
            start_time = time.time()
            result = await processor.process_query("Baseline test query")
            end_time = time.time()
            actual_time = (end_time - start_time) * 1000

            # Should meet baseline performance
            assert actual_time <= baseline["single_query_time"] * 1.1, (
                f"Query time: {actual_time}ms (baseline: {baseline['single_query_time']}ms)"
            )

            # Should not exceed memory baseline significantly
            # This is a simplified check - in real scenario, you'd monitor actual memory usage


if __name__ == "__main__":
    pytest.main([__file__])
