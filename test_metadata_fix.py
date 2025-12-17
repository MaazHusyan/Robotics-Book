#!/usr/bin/env python3
"""
Test script to verify that the metadata fix works properly.
This script tests that source_file and source_location are properly transferred
from ContentChunk to EmbeddingVector.
"""
import sys
import os
from unittest.mock import Mock

# Add the backend/src to the Python path
current_dir = os.path.dirname(__file__)
backend_src_path = os.path.join(current_dir, 'backend', 'src')
sys.path.insert(0, backend_src_path)

# Also add the backend directory to handle relative imports
backend_path = os.path.join(current_dir, 'backend')
sys.path.insert(0, backend_path)

from src.embedding.models.content_models import ContentChunk
from src.embedding.models.embedding_models import EmbeddingVector
from src.embedding.services.cohere_service import CohereEmbeddingService
from src.embedding.services.jina_service import JinaEmbeddingService
from src.embedding.models.embedding_models import EmbeddingConfig


def test_cohere_service_metadata_transfer():
    """Test that Cohere service properly transfers metadata"""
    print("Testing Cohere service metadata transfer...")

    # Create a mock storage to avoid actual API calls
    mock_storage = Mock()
    mock_storage.save_embedding = Mock()

    # Create a mock client to avoid actual API calls
    mock_client = Mock()
    mock_client.embed.return_value = Mock()
    mock_client.embed.return_value.embeddings = [[0.1, 0.2, 0.3, 0.4]]  # Mock embedding vector

    # Create config
    config = EmbeddingConfig(model="test-model")

    # Create service instance
    service = CohereEmbeddingService(config=config, storage_type="qdrant")
    service.storage = mock_storage
    service.client = mock_client

    # Create a content chunk with metadata
    chunk = ContentChunk(
        text="Test content for embedding",
        source_file="test_chapter.md",
        source_location="Chapter 1, Section 2",
        metadata={"chapter": "1", "section": "2", "type": "content"}
    )

    # Process the chunk
    embedding = service.process_content_chunk(chunk)

    # Check that metadata was transferred
    print(f"  Chunk source_file: {chunk.source_file}")
    print(f"  Chunk source_location: {chunk.source_location}")
    print(f"  Embedding metadata: {embedding.metadata}")

    assert embedding.metadata["source_file"] == chunk.source_file, f"Expected {chunk.source_file}, got {embedding.metadata.get('source_file')}"
    assert embedding.metadata["source_location"] == chunk.source_location, f"Expected {chunk.source_location}, got {embedding.metadata.get('source_location')}"

    print("  ✅ Cohere service metadata transfer test passed!")
    return True


def test_jina_service_metadata_transfer():
    """Test that Jina service properly transfers metadata"""
    print("\nTesting Jina service metadata transfer...")

    # Create a mock storage to avoid actual API calls
    mock_storage = Mock()
    mock_storage.save_embedding = Mock()

    # Create a mock response for requests.post
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [{"embedding": [0.1, 0.2, 0.3, 0.4]}]
    }

    # Mock the requests.post function
    import src.embedding.services.jina_service as jina_module
    original_post = jina_module.requests.post
    jina_module.requests.post = Mock(return_value=mock_response)

    # Create config
    config = EmbeddingConfig(model="jina-embeddings-v2")

    try:
        # Create service instance (this will fail without API key, so we'll mock it)
        service = JinaEmbeddingService(config=config, storage_type="qdrant")
        service.storage = mock_storage
        service.api_key = "dummy_key"  # Provide dummy key to bypass validation

        # Create a content chunk with metadata
        chunk = ContentChunk(
            text="Test content for embedding",
            source_file="test_chapter_jina.md",
            source_location="Chapter 3, Section 4",
            metadata={"chapter": "3", "section": "4", "type": "content"}
        )

        # Process the chunk (this will call generate_embedding which makes API call)
        # We need to mock the generate_embedding method to avoid the API call
        original_generate = service.generate_embedding
        def mock_generate(text, model):
            return EmbeddingVector(
                chunk_id=chunk.id,
                vector=[0.1, 0.2, 0.3, 0.4],
                model=model or service.config.model,
                dimensionality=4
            )
        service.generate_embedding = mock_generate

        # Now process the chunk
        embedding = service.process_content_chunk(chunk)

        # Restore original method
        service.generate_embedding = original_generate

        # Check that metadata was transferred
        print(f"  Chunk source_file: {chunk.source_file}")
        print(f"  Chunk source_location: {chunk.source_location}")
        print(f"  Embedding metadata: {embedding.metadata}")

        assert embedding.metadata["source_file"] == chunk.source_file, f"Expected {chunk.source_file}, got {embedding.metadata.get('source_file')}"
        assert embedding.metadata["source_location"] == chunk.source_location, f"Expected {chunk.source_location}, got {embedding.metadata.get('source_location')}"

        print("  ✅ Jina service metadata transfer test passed!")
        return True
    finally:
        # Restore original requests.post
        jina_module.requests.post = original_post


def test_batch_processing():
    """Test that batch processing also transfers metadata"""
    print("\nTesting batch processing metadata transfer...")

    # Create a mock storage to avoid actual API calls
    mock_storage = Mock()
    mock_storage.save_embedding = Mock()

    # Create a mock client to avoid actual API calls
    mock_client = Mock()
    mock_client.embed.return_value = Mock()
    mock_client.embed.return_value.embeddings = [
        [0.1, 0.2, 0.3, 0.4],
        [0.5, 0.6, 0.7, 0.8]
    ]  # Mock embedding vectors

    # Create config
    config = EmbeddingConfig(model="test-model", batch_size=2)

    # Create service instance
    service = CohereEmbeddingService(config=config, storage_type="qdrant")
    service.storage = mock_storage
    service.client = mock_client

    # Create content chunks with metadata
    chunks = [
        ContentChunk(
            text="First test content",
            source_file="chapter1.md",
            source_location="Chapter 1, Section 1",
            metadata={"chapter": "1", "section": "1"}
        ),
        ContentChunk(
            text="Second test content",
            source_file="chapter2.md",
            source_location="Chapter 2, Section 1",
            metadata={"chapter": "2", "section": "1"}
        )
    ]

    # Process the chunks in batch
    embeddings = service.process_content_batch(chunks)

    # Check that metadata was transferred for each chunk
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        print(f"  Chunk {i+1} source_file: {chunk.source_file}")
        print(f"  Chunk {i+1} source_location: {chunk.source_location}")
        print(f"  Embedding {i+1} metadata: {embedding.metadata}")

        assert embedding.metadata["source_file"] == chunk.source_file, f"Expected {chunk.source_file}, got {embedding.metadata.get('source_file')}"
        assert embedding.metadata["source_location"] == chunk.source_location, f"Expected {chunk.source_location}, got {embedding.metadata.get('source_location')}"

    print("  ✅ Batch processing metadata transfer test passed!")
    return True


if __name__ == "__main__":
    print("Testing metadata transfer fix...")
    print("=" * 50)

    try:
        test_cohere_service_metadata_transfer()
        test_jina_service_metadata_transfer()
        test_batch_processing()

        print("\n🎉 All tests passed! The metadata transfer fix is working correctly.")
        print("✅ source_file and source_location will now be properly stored in Qdrant embeddings.")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)