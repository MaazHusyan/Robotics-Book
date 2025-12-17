#!/usr/bin/env python3
"""
Simple test script to verify Qdrant collection creation and basic functionality
"""
import os
import sys
from pathlib import Path

# Add the backend/src to the Python path (running from project root)
backend_src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(backend_src_path))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from src.utils.qdrant_storage import QdrantEmbeddingStorage

def test_qdrant_collection():
    """
    Test creating and verifying the All_Book_Chapters collection in Qdrant
    """
    print("🧪 Testing Qdrant Collection Creation")
    print("=" * 40)

    # Create Qdrant storage instance with the target collection name
    storage = QdrantEmbeddingStorage(collection_name="All_Book_Chapters", vector_size=1024)

    print(f"📦 Creating/accessing collection: All_Book_Chapters")

    try:
        # This will trigger the creation of the collection if it doesn't exist
        storage._ensure_collection_exists()
        print("✅ Collection 'All_Book_Chapters' is ready in Qdrant")

        # Test getting collection info
        try:
            collection_info = storage.client.get_collection("All_Book_Chapters")
            print(f"📊 Collection details:")
            print(f"   - Points count: {collection_info.points_count}")
            print(f"   - Vector size: {collection_info.config.params.size}")
            print(f"   - Distance: {collection_info.config.params.distance}")
        except Exception as e:
            print(f"⚠️  Could not get collection details: {e}")

        print("✅ Qdrant collection test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error with Qdrant collection: {e}")
        return False

if __name__ == "__main__":
    test_qdrant_collection()