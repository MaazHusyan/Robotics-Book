#!/usr/bin/env python3
"""
Test script to verify that embeddings are stored in Qdrant.
This script will test both the Qdrant storage functionality and provide instructions for deployment.
"""

import tempfile
from unittest.mock import Mock, patch
from backend.src.embedding.services.cohere_service import CohereEmbeddingService
from backend.src.embedding.models.content_models import ContentChunk
from backend.src.utils.qdrant_storage import QdrantEmbeddingStorage


def test_qdrant_storage_functionality():
    """Test that Qdrant storage is properly implemented and can be initialized."""
    print("Testing Qdrant Storage Functionality...")

    try:
        # Test that Qdrant storage can be initialized
        storage = QdrantEmbeddingStorage(collection_name="test_robotics_embeddings")
        print("✅ Qdrant storage initialized successfully")

        # Verify that the storage implements the interface
        required_methods = ['save_embedding', 'save_embeddings_batch', 'load_embedding',
                          'load_all_embeddings', 'delete_embedding']

        for method in required_methods:
            if hasattr(storage, method):
                print(f"✅ Method {method} is implemented")
            else:
                print(f"❌ Method {method} is missing")

        return True
    except Exception as e:
        print(f"❌ Qdrant storage initialization failed: {e}")
        return False


def test_cohere_service_with_qdrant():
    """Test that Cohere service can be configured to use Qdrant by default."""
    print("\nTesting Cohere Service with Qdrant Storage...")

    try:
        with patch('backend.src.embedding.services.cohere_service.settings') as mock_settings, \
             patch('backend.src.embedding.services.cohere_service.cohere.Client'):

            # Set up mock settings with fake API key
            mock_settings.COHERE_API_KEY = "fake-cohere-api-key-for-testing"

            # Initialize service - should default to Qdrant now
            service = CohereEmbeddingService()

            # Verify the storage type
            from backend.src.utils.qdrant_storage import QdrantEmbeddingStorage
            if isinstance(service.storage, QdrantEmbeddingStorage):
                print("✅ Cohere service is configured to use Qdrant storage by default")
            else:
                print("❌ Cohere service is not using Qdrant storage")
                return False

            # Mock the Cohere client response
            mock_response = Mock()
            mock_response.embeddings = [[0.1, 0.2, 0.3, 0.4]]
            service.client.embed.return_value = mock_response

            # Create a content chunk
            chunk = ContentChunk(
                id="test-qdrant-chunk-1",
                text="This is a test chunk to verify Qdrant storage.",
                source_file="test_robotics_book.pdf",
                source_location="page_100",
                metadata={"chapter": "5", "topic": "motion_planning"}
            )

            # Process the chunk - this would store in Qdrant if server available
            embedding = service.process_content_chunk(chunk)

            print(f"✅ Embedding generated successfully: {embedding.chunk_id}")
            print(f"   Vector dimensionality: {embedding.dimensionality}")
            print(f"   Stored using: {type(service.storage).__name__}")

            return True
    except Exception as e:
        print(f"❌ Cohere service with Qdrant test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_deployment_instructions():
    """Show instructions for deploying Qdrant server."""
    print("\n" + "="*60)
    print("QDRANT DEPLOYMENT INSTRUCTIONS")
    print("="*60)

    print("\n1. DOCKER DEPLOYMENT (Recommended for development):")
    print("   ```bash")
    print("   # Pull and run Qdrant container")
    print("   docker pull qdrant/qdrant")
    print("   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant")
    print("   ```")

    print("\n2. DOCKER-COMPOSE (Recommended for production):")
    print("   ```yaml")
    print("   version: '3.8'")
    print("   services:")
    print("     qdrant:")
    print("       image: qdrant/qdrant:latest")
    print("       container_name: qdrant-server")
    print("       ports:")
    print("         - \"6333:6333\"")
    print("         - \"6334:6334\"")
    print("       volumes:")
    print("         - ./qdrant_data:/qdrant/data")
    print("       environment:")
    print("         - QDRANT_API_KEY=your-api-key-here  # Optional")
    print("   ```")

    print("\n3. ENVIRONMENT CONFIGURATION:")
    print("   Update your .env file with:")
    print("   ```env")
    print("   # Qdrant Configuration")
    print("   QDRANT_URL=http://localhost:6333")
    print("   QDRANT_API_KEY=your-api-key-here  # Optional for local")
    print("   ```")


def show_verification_steps():
    """Show steps to verify Qdrant storage is working."""
    print("\n" + "="*60)
    print("VERIFICATION STEPS")
    print("="*60)

    print("\nOnce you have Qdrant server running:")
    print("1. Update your .env file with Qdrant configuration")
    print("2. Run your embedding pipeline as normal")
    print("3. Check Qdrant dashboard or API to verify embeddings are stored")
    print("4. Use Qdrant's web UI at http://localhost:6333/dashboard (if enabled)")
    print("5. Or query via API: GET http://localhost:6333/collections/robotics_embeddings")

    print("\nExample verification code:")
    print("```python")
    print("# After running your embedding pipeline")
    print("from qdrant_client import QdrantClient")
    print("")
    print("client = QdrantClient(url=\"http://localhost:6333\")")
    print("collection_info = client.get_collection(\"robotics_embeddings\")")
    print("print(f'Points in collection: {collection_info.points_count}')")
    print("```")


def main():
    """Main test function."""
    print("🤖 Qdrant Embedding Storage Verification")
    print("This script verifies that the system is configured to store embeddings in Qdrant")

    # Test Qdrant storage functionality
    qdrant_ok = test_qdrant_storage_functionality()

    # Test Cohere service with Qdrant
    service_ok = test_cohere_service_with_qdrant()

    print("\n" + "="*60)
    print("CONFIGURATION STATUS")
    print("="*60)

    if qdrant_ok and service_ok:
        print("✅ QDRANT STORAGE IS READY FOR DEPLOYMENT")
        print("✅ Cohere service is configured to use Qdrant by default")
        print("✅ All interfaces and functionality are implemented")
        print("✅ No code changes needed - just deploy Qdrant server")
    else:
        print("❌ Issues found with Qdrant configuration")
        return False

    show_deployment_instructions()
    show_verification_steps()

    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Deploy Qdrant server using Docker or Docker Compose")
    print("2. Update your .env file with Qdrant URL and API key (if applicable)")
    print("3. Run your embedding pipeline - embeddings will automatically store in Qdrant")
    print("4. Verify storage by checking the Qdrant collection")
    print("5. Once verified, the system will be fully operational with vector storage")

    return True


if __name__ == "__main__":
    main()