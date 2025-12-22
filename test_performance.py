"""
Performance test to ensure <5s response time requirement for the chatbot agent.
"""
import asyncio
import time
import statistics
from typing import List, Tuple

from backend.src.models.agent_models import AgentConfig, ChatRequest
from backend.src.services.rag_integration_service import RAGIntegrationService
from backend.src.utils.qdrant_retriever import QdrantRetriever
from backend.src.services.agent_service import AgentService
from backend.src.config import get_settings


async def performance_test():
    """
    Run performance tests to ensure response time requirements are met.
    """
    print("Starting performance tests...")

    # Initialize services
    settings = get_settings()

    try:
        from backend.src.retrieval.utils.qdrant_retriever import QdrantRetriever
    except ImportError:
        try:
            from backend.src.retrieval.qdrant_retriever import QdrantRetriever
        except ImportError:
            from backend.src.utils.qdrant_retriever import QdrantRetriever

    qdrant_retriever = QdrantRetriever(
        url=settings.qdrant_url,
        collection_name=settings.qdrant_collection_name
    )

    rag_service = RAGIntegrationService(qdrant_retriever)

    # Create agent configuration
    agent_config = AgentConfig(
        model_name=settings.model_name if hasattr(settings, 'model_name') else "gemini-2.5-flash",
        temperature=settings.temperature if hasattr(settings, 'temperature') else 0.7,
        max_tokens=settings.max_tokens if hasattr(settings, 'max_tokens') else 1000,
        top_k=settings.top_k if hasattr(settings, 'top_k') else 5,
        min_relevance_score=settings.min_relevance_score if hasattr(settings, 'min_relevance_score') else 0.5,
        enable_tracing=settings.enable_tracing if hasattr(settings, 'enable_tracing') else False,
        timeout_seconds=settings.timeout_seconds if hasattr(settings, 'timeout_seconds') else 30
    )

    # Create the agent service
    agent_service = AgentService(config=agent_config, rag_service=rag_service)

    # Test queries
    test_queries = [
        "What is forward kinematics?",
        "Explain robot dynamics",
        "How do I control a robotic arm?",
        "What are the different types of robot joints?",
        "Describe the difference between forward and inverse kinematics",
        "What is a Jacobian matrix in robotics?",
        "Explain PID control for robots",
        "What is path planning in robotics?"
    ]

    response_times = []
    successful_requests = 0
    failed_requests = 0

    print(f"Running {len(test_queries)} test queries...")

    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}/{len(test_queries)}: {query}")

        start_time = time.time()
        try:
            response = await agent_service.process_message(
                message=query,
                require_sources=True
            )
            end_time = time.time()

            response_time = end_time - start_time
            response_times.append(response_time)

            print(f"  Response time: {response_time:.2f}s - {'PASS' if response_time < 5.0 else 'FAIL (>' + str(5.0) + 's)'}")

            if response_time < 5.0:
                successful_requests += 1
            else:
                failed_requests += 1

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)

            print(f"  Error: {str(e)} - Response time: {response_time:.2f}s - FAIL")
            failed_requests += 1

    # Calculate statistics
    if response_times:
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        p95_response_time = sorted(response_times)[int(0.95 * len(response_times))] if len(response_times) > 1 else response_times[0]

        print("\n" + "="*60)
        print("PERFORMANCE TEST RESULTS")
        print("="*60)
        print(f"Total requests: {len(test_queries)}")
        print(f"Successful: {successful_requests}")
        print(f"Failed: {failed_requests}")
        print(f"Success rate: {(successful_requests/len(test_queries)*100):.1f}%")
        print()
        print("Response Time Statistics:")
        print(f"  Average: {avg_response_time:.2f}s")
        print(f"  Median: {median_response_time:.2f}s")
        print(f"  Min: {min_response_time:.2f}s")
        print(f"  Max: {max_response_time:.2f}s")
        print(f"  95th percentile: {p95_response_time:.2f}s")
        print()

        # Check if requirements are met
        requirement_met = avg_response_time < 5.0 and max_response_time < 5.0
        print(f"Requirement (<5s response time): {'PASS' if requirement_met else 'FAIL'}")

        if not requirement_met:
            print("  - Average response time requirement: " + ("PASS" if avg_response_time < 5.0 else "FAIL"))
            print("  - Maximum response time requirement: " + ("PASS" if max_response_time < 5.0 else "FAIL"))

        print("="*60)

        return requirement_met, response_times
    else:
        print("No responses recorded - test failed")
        return False, []


async def load_test(concurrent_users: int = 5, queries_per_user: int = 3):
    """
    Simulate concurrent users to test performance under load.
    """
    print(f"\nRunning load test with {concurrent_users} concurrent users, {queries_per_user} queries each...")

    # Initialize services for each simulated user
    tasks = []
    for user_id in range(concurrent_users):
        user_queries = [
            "What is forward kinematics?",
            "Explain robot dynamics",
            "How do I control a robotic arm?"
        ][:queries_per_user]

        for query in user_queries:
            task = asyncio.create_task(single_request(query))
            tasks.append(task)

    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()

    total_time = end_time - start_time
    successful = sum(1 for r in results if not isinstance(r, Exception))
    failed = len(results) - successful

    print(f"Load test completed in {total_time:.2f}s")
    print(f"Successful requests: {successful}")
    print(f"Failed requests: {failed}")
    print(f"Requests per second: {len(results)/total_time:.2f}")


async def single_request(query: str):
    """
    Helper function for load testing.
    """
    settings = get_settings()

    try:
        from backend.src.retrieval.utils.qdrant_retriever import QdrantRetriever
    except ImportError:
        try:
            from backend.src.retrieval.qdrant_retriever import QdrantRetriever
        except ImportError:
            from backend.src.utils.qdrant_retriever import QdrantRetriever

    qdrant_retriever = QdrantRetriever(
        url=settings.qdrant_url,
        collection_name=settings.qdrant_collection_name
    )

    rag_service = RAGIntegrationService(qdrant_retriever)

    agent_config = AgentConfig(
        model_name="gemini-2.5-flash",
        temperature=0.7,
        max_tokens=1000,
        top_k=5,
        min_relevance_score=0.5,
        timeout_seconds=30
    )

    agent_service = AgentService(config=agent_config, rag_service=rag_service)

    start_time = time.time()
    response = await agent_service.process_message(message=query, require_sources=True)
    end_time = time.time()

    return {
        'query': query,
        'response_time': end_time - start_time,
        'response_length': len(response.response)
    }


if __name__ == "__main__":
    print("Running performance tests for Chatbot Agent Integration...")
    print("Note: This test requires a running Qdrant instance with robotics content")
    print("and valid API keys configured in environment variables.\n")

    # Run basic performance test
    requirement_met, response_times = asyncio.run(performance_test())

    # Optionally run load test (uncomment to run)
    # print("\n" + "="*60)
    # asyncio.run(load_test(concurrent_users=3, queries_per_user=2))

    print(f"\nPerformance test completed. Requirement met: {requirement_met}")