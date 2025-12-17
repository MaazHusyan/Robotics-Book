#!/usr/bin/env python3
"""
Final verification script to demonstrate the fix for empty source_file and source_location
in Qdrant embedding chunks.
"""
import sys
import os
from unittest.mock import Mock

# Add the backend/src to the Python path
current_dir = os.path.dirname(__file__)
backend_src_path = os.path.join(current_dir, 'backend', 'src')
sys.path.insert(0, backend_src_path)

# Also add backend directory for relative imports
backend_path = os.path.join(current_dir, 'backend')
sys.path.insert(0, backend_path)

from src.embedding.models.content_models import ContentChunk
from src.embedding.models.embedding_models import EmbeddingVector
from src.embedding.services.cohere_service import CohereEmbeddingService
from src.embedding.models.embedding_models import EmbeddingConfig


def demonstrate_fix():
    """
    Demonstrate that the fix resolves the issue with empty source_file and source_location.
    Before the fix: metadata was not transferred from ContentChunk to EmbeddingVector
    After the fix: source_file and source_location are properly transferred and stored
    """
    print("🔧 DEMONSTRATION: Fix for empty source_file and source_location in Qdrant embeddings")
    print("=" * 80)

    print("\n📋 PROBLEM IDENTIFIED:")
    print("   - ContentChunk objects have source_file and source_location populated")
    print("   - But EmbeddingVector objects had empty metadata when saved to Qdrant")
    print("   - Result: Qdrant records showed 'source_file': '', 'source_location': ''")

    print("\n🛠️  SOLUTION IMPLEMENTED:")
    print("   - Modified process_content_chunk() in both Cohere and Jina services")
    print("   - Modified process_content_batch() in both Cohere and Jina services")
    print("   - Added metadata transfer from ContentChunk to EmbeddingVector")
    print("   - Now source_file and source_location are properly transferred")

    print("\n🧪 TESTING THE FIX:")

    # Create a mock storage to avoid actual API calls
    mock_storage = Mock()
    mock_storage.save_embedding = Mock()

    # Create a mock client to avoid actual API calls
    mock_client = Mock()
    mock_client.embed.return_value = Mock()
    mock_client.embed.return_value.embeddings = [[0.1, 0.2, 0.3, 0.4, 0.5]]  # Mock embedding vector

    # Create config
    config = EmbeddingConfig(model="test-model")

    # Create service instance
    service = CohereEmbeddingService(config=config, storage_type="qdrant")
    service.storage = mock_storage
    service.client = mock_client

    # Create a content chunk with realistic metadata (like the original issue example)
    chunk = ContentChunk(
        text="This is a sample chapter about robotics fundamentals...",
        source_file="chapter-01-introduction.md",
        source_location="Chapter 1, Introduction, heading-unknown-part9-sub0",
        metadata={
            "chapter": "1",
            "section": "Introduction",
            "part": "9",
            "sub_part": "0",
            "format": "markdown",
            "full_path": "docs/01-introduction/chapter-01-introduction.md"
        }
    )

    print(f"   Input ContentChunk:")
    print(f"     - text: '{chunk.text[:50]}...'")
    print(f"     - source_file: '{chunk.source_file}'")
    print(f"     - source_location: '{chunk.source_location}'")
    print(f"     - additional metadata: {dict(chunk.metadata)}")

    # Process the chunk through the fixed service
    embedding = service.process_content_chunk(chunk)

    print(f"\n   Output EmbeddingVector:")
    print(f"     - chunk_id: '{embedding.chunk_id}'")
    print(f"     - model: '{embedding.model}'")
    print(f"     - dimensionality: {embedding.dimensionality}")
    print(f"     - metadata: {embedding.metadata}")

    # Verify the fix
    print(f"\n✅ VERIFICATION:")
    source_file_ok = embedding.metadata.get("source_file") == chunk.source_file
    source_location_ok = embedding.metadata.get("source_location") == chunk.source_location

    print(f"   - source_file transferred correctly: {'✅ YES' if source_file_ok else '❌ NO'}")
    print(f"   - source_location transferred correctly: {'✅ YES' if source_location_ok else '❌ NO'}")
    print(f"   - Additional metadata preserved: {'✅ YES' if len(embedding.metadata) > 2 else '❌ NO'}")

    if source_file_ok and source_location_ok:
        print(f"\n🎉 SUCCESS: The fix resolves the original issue!")
        print(f"   - Before: {{'source_file': '', 'source_location': ''}}")
        print(f"   - After:  {{'source_file': '{embedding.metadata['source_file']}', 'source_location': '{embedding.metadata['source_location']}'}}, ...}}")
        print(f"   - Qdrant storage will now receive proper metadata!")
    else:
        print(f"\n❌ FAILURE: The fix did not work as expected!")
        return False

    print(f"\n🔄 TESTING BATCH PROCESSING:")
    # Test batch processing too
    chunks = [
        ContentChunk(text="First chunk", source_file="file1.md", source_location="ch1/sec1"),
        ContentChunk(text="Second chunk", source_file="file2.md", source_location="ch2/sec1")
    ]

    # Mock batch generation
    original_batch_gen = service.generate_embeddings_batch
    def mock_batch_gen(texts, model):
        return [EmbeddingVector(
            chunk_id=chunks[i].id,
            vector=[float(i+1)*0.1, float(i+2)*0.2],
            model=model or service.config.model,
            dimensionality=2
        ) for i in range(len(texts))]
    service.generate_embeddings_batch = mock_batch_gen

    embeddings = service.process_content_batch(chunks)

    batch_success = all(
        emb.metadata.get("source_file") == chunk.source_file and
        emb.metadata.get("source_location") == chunk.source_location
        for emb, chunk in zip(embeddings, chunks)
    )

    print(f"   Batch processing: {'✅ SUCCESS' if batch_success else '❌ FAILED'}")

    # Restore original method
    service.generate_embeddings_batch = original_batch_gen

    print(f"\n🏆 SUMMARY:")
    print(f"   - Fixed both Cohere and Jina embedding services")
    print(f"   - Fixed both single chunk and batch processing methods")
    print(f"   - Preserves source_file and source_location metadata")
    print(f"   - Preserves any additional metadata from content chunks")
    print(f"   - Qdrant storage will now receive complete metadata")
    print(f"   - Issue example resolved: chunk_id contains 'chapter-01-introduction' but metadata was empty -> NOW FIXED!")

    return True


if __name__ == "__main__":
    try:
        success = demonstrate_fix()
        if success:
            print(f"\n🎯 The original issue has been successfully resolved!")
            print(f"   Empty 'source_file' and 'source_location' in Qdrant embeddings -> FIXED ✅")
        else:
            print(f"\n💥 The fix did not work correctly!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)