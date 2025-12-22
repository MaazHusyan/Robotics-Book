"""
Qdrant retriever utility adapted from qdrant_retrieve.py reference file.

This module provides Qdrant connection and retrieval patterns for the RAG chatbot system.
"""
import os
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from src.config import settings


def retrieve_data_from_qdrant_collection(
    collection_name: str = None,
    query_vector: List[float] = None,
    limit: int = 10,
    filters: Dict = None,
    with_payload: bool = True,
    with_vectors: bool = False
) -> List[Dict]:
    """
    Retrieve data from a specified collection in Qdrant cluster.
    This function adapts the implementation from qdrant_retrieve.py with settings integration.

    Args:
        collection_name: Name of the collection to retrieve data from (uses settings default if None)
        query_vector: Vector to search for similarity (if None, performs scroll operation)
        limit: Maximum number of results to return
        filters: Dictionary with filter conditions (e.g., {"genre": "fiction"})
        with_payload: Whether to include payload data in results
        with_vectors: Whether to include vector data in results

    Returns:
        List of retrieved records
    """
    if collection_name is None:
        collection_name = settings.QDRANT_COLLECTION_NAME

    # Get connection details from settings
    qdrant_url = settings.QDRANT_URL
    api_key = settings.QDRANT_API_KEY

    # Initialize Qdrant client with timeout settings
    if "https://" in qdrant_url or "http://" in qdrant_url:
        # Handle cloud instance with URL
        client = QdrantClient(
            url=qdrant_url,
            api_key=api_key,
            prefer_grpc=True,
            timeout=30  # 30 second timeout
        )
    elif api_key:
        # Handle authenticated instance - extract host and port from URL
        import urllib.parse
        parsed = urllib.parse.urlparse(qdrant_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6333

        client = QdrantClient(
            host=host,
            port=port,
            api_key=api_key,
            grpc_port=6334,
            prefer_grpc=True,
            timeout=30  # 30 second timeout
        )
    else:
        # Handle local instance - extract host and port from URL
        import urllib.parse
        parsed = urllib.parse.urlparse(qdrant_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6333

        client = QdrantClient(
            host=host,
            port=port,
            timeout=30  # 30 second timeout
        )

    try:
        if query_vector is not None:
            # Perform similarity search using the newer query_points method for vector search
            search_results = client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit,
                with_payload=with_payload,
                with_vectors=with_vectors
            )

            # Convert results to dictionary format
            records = []
            # Check if search_results is a list or has a points attribute
            if hasattr(search_results, 'points'):
                # If it's a response object with points attribute
                search_points = search_results.points
            else:
                # If it's already a list
                search_points = search_results

            for result in search_points:
                record = {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload if result.payload else {}
                }
                if with_vectors:
                    record["vector"] = result.vector
                records.append(record)

            return records
        else:
            # Perform scroll operation to get all records (without similarity search)
            records, _ = client.scroll(
                collection_name=collection_name,
                limit=limit,
                with_payload=with_payload,
                with_vectors=with_vectors
            )

            # Convert results to dictionary format
            formatted_records = []
            for record in records:
                formatted_record = {
                    "id": record.id,
                    "payload": record.payload if record.payload else {}
                }
                if with_vectors:
                    formatted_record["vector"] = record.vector
                formatted_records.append(formatted_record)

            return formatted_records

    except Exception as e:
        print(f"Error retrieving data from collection '{collection_name}': {e}")
        return []


def get_qdrant_client() -> QdrantClient:
    """
    Get a Qdrant client instance configured with settings.

    Returns:
        Configured QdrantClient instance
    """
    qdrant_url = settings.QDRANT_URL
    api_key = settings.QDRANT_API_KEY

    # Initialize Qdrant client with timeout settings
    if "https://" in qdrant_url or "http://" in qdrant_url:
        # Handle cloud instance with URL
        client = QdrantClient(
            url=qdrant_url,
            api_key=api_key,
            prefer_grpc=True,
            timeout=30  # 30 second timeout
        )
    elif api_key:
        # Handle authenticated instance - extract host and port from URL
        import urllib.parse
        parsed = urllib.parse.urlparse(qdrant_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6333

        client = QdrantClient(
            host=host,
            port=port,
            api_key=api_key,
            grpc_port=6334,
            prefer_grpc=True,
            timeout=30  # 30 second timeout
        )
    else:
        # Handle local instance - extract host and port from URL
        import urllib.parse
        parsed = urllib.parse.urlparse(qdrant_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6333

        client = QdrantClient(
            host=host,
            port=port,
            timeout=30  # 30 second timeout
        )

    return client