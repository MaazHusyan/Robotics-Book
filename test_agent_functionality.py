"""
Test script for end-to-end chat functionality with sample queries.

This script tests the agent integration with sample robotics questions.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to Python path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.models.agent_models import AgentConfig, ChatRequest
from src.retrieval.services.rag_integration_service import RAGIntegrationService
from src.retrieval.utils.qdrant_retriever import QdrantRetriever  # Assuming it's in utils
from src.services.agent_service import AgentService
from src.config import get_settings


async def test_agent_functionality():
    """
    Test the agent functionality with sample queries.
    """
    print("Starting agent functionality test...")

    # Initialize services
    settings = get_settings()

    # Initialize the RAG integration service
    rag_service = RAGIntegrationService()

    # Create agent configuration
    agent_config = AgentConfig(
        model_name=settings.MODEL if settings.MODEL else "gemini/gemini-2.5-flash",
        temperature=0.7,  # Default value
        max_tokens=1000,  # Default value
        top_k=5,  # Default value
        min_relevance_score=0.5,  # Default value
        enable_tracing=getattr(settings, 'enable_tracing', False),
        timeout_seconds=30  # Default value
    )

    # Create the agent service
    agent_service = AgentService(config=agent_config, rag_service=rag_service)

    # Sample queries to test
    sample_queries = [
        "What is forward kinematics?",
        "Explain robot dynamics",
        "How do I control a robotic arm?",
        "What are the different types of robot joints?",
        "Describe the difference between forward and inverse kinematics"
    ]

    print(f"Testing {len(sample_queries)} sample queries...")

    for i, query in enumerate(sample_queries, 1):
        print(f"\n--- Test {i}: {query} ---")

        try:
            # Process the message
            response = await agent_service.process_message(
                message=query,
                session_id=None,  # New session for each test
                require_sources=True
            )

            print(f"Response: {response.response[:200]}...")
            print(f"Sources found: {len(response.sources)}")
            print(f"Response time: {response.response_time:.2f}s")
            print(f"Conversation turn: {response.conversation_turn}")

            if response.error:
                print(f"Error: {response.error}")

        except Exception as e:
            print(f"Error processing query '{query}': {str(e)}")

    print("\n--- Multi-turn conversation test ---")

    # Test multi-turn conversation
    try:
        # First message
        response1 = await agent_service.process_message(
            message="What is forward kinematics?",
            require_sources=True
        )
        print(f"First response session: {response1.session_id}")
        print(f"First response: {response1.response[:100]}...")

        # Follow-up message using the same session
        response2 = await agent_service.process_message(
            message="Can you explain it in simpler terms?",
            session_id=response1.session_id,
            require_sources=True
        )
        print(f"Second response: {response2.response[:100]}...")
        print(f"Same session: {response1.session_id == response2.session_id}")

    except Exception as e:
        print(f"Error in multi-turn test: {str(e)}")

    print("\nAgent functionality test completed.")


if __name__ == "__main__":
    asyncio.run(test_agent_functionality())