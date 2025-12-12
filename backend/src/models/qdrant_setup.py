from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise ValueError("QDRANT_URL and QDRANT_API_KEY environment variables are required")

logger = logging.getLogger(__name__)

def get_qdrant_client():
    """Get Qdrant client instance"""
    try:
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY
        )
        logger.info("Qdrant client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant client: {e}")
        raise

def create_collection():
    """Create content_vectors collection for 768-dimension embeddings"""
    client = get_qdrant_client()
    collection_name = "content_vectors"
    
    try:
        # Check if collection exists
        collections = client.get_collections().collections
        collection_exists = any(
            collection.name == collection_name 
            for collection in collections
        )
        
        if collection_exists:
            logger.info(f"Collection '{collection_name}' already exists")
            return True
        
        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=768,  # Gemini embedding dimensions
                distance=Distance.COSINE
            )
        )
        logger.info(f"Collection '{collection_name}' created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create collection: {e}")
        return False

def test_collection():
    """Test Qdrant collection access"""
    try:
        client = get_qdrant_client()
        collection_info = client.get_collection("content_vectors")
        logger.info(f"Collection info: {collection_info}")
        return True
    except Exception as e:
        logger.error(f"Failed to access collection: {e}")
        return False

if __name__ == "__main__":
    # Test connection and create collection
    if test_collection():
        print("Qdrant connection successful")
        create_collection()
        print("Qdrant setup complete")
    else:
        print("Qdrant connection failed")
