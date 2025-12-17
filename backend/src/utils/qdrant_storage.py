import uuid
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import sys
import os

# Add the src directory to the path for relative imports
src_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, src_path)

from config import settings
from src.embedding.models.embedding_models import EmbeddingVector
from src.utils.storage_interface import EmbeddingStorageInterface


class QdrantEmbeddingStorage(EmbeddingStorageInterface):
    """
    Qdrant-based storage for embedding vectors.
    This replaces the temporary file-based storage with a proper vector database.
    """

    def __init__(self, collection_name: str = "robotics_embeddings", vector_size: int = 1024):
        """
        Initialize the Qdrant embedding storage.

        Args:
            collection_name: Name of the Qdrant collection to store embeddings
            vector_size: Size of the vectors (will be auto-detected from first embedding if not specified)
        """
        # Initialize Qdrant client with configuration from settings
        if settings.QDRANT_API_KEY:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                prefer_grpc=True
            )
        else:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                prefer_grpc=True
            )

        self.collection_name = collection_name
        self.vector_size = vector_size
        self._collection_exists = False  # Track if collection has been verified

    def _ensure_collection_exists(self, vector_size: int = None):
        """
        Ensure the collection exists in Qdrant with proper configuration.
        If it doesn't exist, create it with appropriate vector parameters.
        If Qdrant is unavailable, log the issue but don't raise an exception.

        Args:
            vector_size: Size of vectors for the collection (uses self.vector_size if not provided)
        """
        try:
            # Try to get collection info
            self.client.get_collection(self.collection_name)
            self._collection_exists = True
        except Exception as e:
            # Check if this is a connection error (Qdrant server not available)
            if "Connection refused" in str(e) or "UNAVAILABLE" in str(e) or "failed to connect" in str(e):
                # Qdrant server is not available, log and continue
                print(f"⚠️  Qdrant server not available: {e}")
                print("⚠️  Embeddings will not be stored in Qdrant until server is available")
                return  # Don't create collection if server is not available
            else:
                # Collection doesn't exist, create it
                # Use the provided vector size or fall back to the default
                size = vector_size or self.vector_size

                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=size, distance=Distance.COSINE),
                )
                self._collection_exists = True

    def save_embedding(self, embedding: EmbeddingVector) -> str:
        """
        Save a single embedding vector to Qdrant.

        Args:
            embedding: The embedding vector to save

        Returns:
            The ID of the point in Qdrant where the embedding was stored
        """
        # Ensure collection exists with the correct vector size
        if not self._collection_exists:
            self._ensure_collection_exists(len(embedding.vector) if embedding.vector else self.vector_size)

        # If collection still doesn't exist (server unavailable), return a placeholder ID
        if not self._collection_exists:
            # Qdrant server is not available, return a placeholder ID
            return f"qdrant_unavailable_{str(uuid.uuid4())}"

        # Generate a unique ID for this embedding
        point_id = str(uuid.uuid4())

        # Prepare the payload with embedding metadata
        payload = {
            "chunk_id": embedding.chunk_id,
            "model": embedding.model,
            "dimensionality": embedding.dimensionality,
            "source_file": embedding.metadata.get("source_file", "") if embedding.metadata else "",
            "source_location": embedding.metadata.get("source_location", "") if embedding.metadata else "",
        }

        # Add any additional metadata from the embedding
        if embedding.metadata:
            for key, value in embedding.metadata.items():
                if key not in payload:
                    payload[key] = value

        # Prepare the point structure
        point = PointStruct(
            id=point_id,
            vector=embedding.vector,
            payload=payload
        )

        # Upload the point to Qdrant
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
        except Exception as e:
            print(f"⚠️  Failed to save embedding to Qdrant: {e}")
            return f"qdrant_error_{str(uuid.uuid4())}"

        return point_id

    def save_embeddings_batch(self, embeddings: List[EmbeddingVector]) -> List[str]:
        """
        Save a batch of embedding vectors to Qdrant.

        Args:
            embeddings: List of embedding vectors to save

        Returns:
            List of IDs of the points in Qdrant where embeddings were stored
        """
        if not embeddings:
            return []

        # Ensure collection exists with the correct vector size based on first embedding
        if not self._collection_exists:
            first_vector_size = len(embeddings[0].vector) if embeddings[0].vector else self.vector_size
            self._ensure_collection_exists(first_vector_size)

        # If collection still doesn't exist (server unavailable), return placeholder IDs
        if not self._collection_exists:
            # Qdrant server is not available, return placeholder IDs
            return [f"qdrant_unavailable_{str(uuid.uuid4())}" for _ in embeddings]

        point_ids = []
        points = []

        for embedding in embeddings:
            # Generate a unique ID for this embedding
            point_id = str(uuid.uuid4())
            point_ids.append(point_id)

            # Prepare the payload with embedding metadata
            payload = {
                "chunk_id": embedding.chunk_id,
                "model": embedding.model,
                "dimensionality": embedding.dimensionality,
                "source_file": embedding.metadata.get("source_file", "") if embedding.metadata else "",
                "source_location": embedding.metadata.get("source_location", "") if embedding.metadata else "",
            }

            # Add any additional metadata from the embedding
            if embedding.metadata:
                for key, value in embedding.metadata.items():
                    if key not in payload:
                        payload[key] = value

            # Prepare the point structure
            point = PointStruct(
                id=point_id,
                vector=embedding.vector,
                payload=payload
            )

            points.append(point)

        # Upload all points to Qdrant in a batch
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        except Exception as e:
            print(f"⚠️  Failed to save embeddings batch to Qdrant: {e}")
            return [f"qdrant_error_{str(uuid.uuid4())}" for _ in embeddings]

        return point_ids

    def load_embedding(self, point_id: str) -> Optional[EmbeddingVector]:
        """
        Load a single embedding vector from Qdrant by its point ID.

        Args:
            point_id: The ID of the point in Qdrant

        Returns:
            The loaded embedding vector or None if not found
        """
        # If collection doesn't exist (server unavailable), return None
        if not self._collection_exists:
            return None

        try:
            records = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id]
            )

            if not records:
                return None

            record = records[0]

            # Create and return the EmbeddingVector
            return EmbeddingVector(
                chunk_id=record.payload.get("chunk_id", ""),
                vector=record.vector,
                model=record.payload.get("model", ""),
                dimensionality=record.payload.get("dimensionality", len(record.vector) if record.vector else 0),
                metadata={k: v for k, v in record.payload.items()
                         if k not in ["chunk_id", "model", "dimensionality"]}
            )
        except Exception:
            return None

    def search_similar(self, query_vector: List[float], limit: int = 10,
                      filters: Optional[Dict[str, Any]] = None) -> List[EmbeddingVector]:
        """
        Search for similar embeddings in Qdrant.

        Args:
            query_vector: The vector to search for similar embeddings to
            limit: Maximum number of results to return
            filters: Optional filters to apply to the search

        Returns:
            List of similar embedding vectors
        """
        # Ensure collection exists before searching
        if not self._collection_exists:
            self._ensure_collection_exists(len(query_vector) if query_vector else self.vector_size)

        # If collection still doesn't exist (server unavailable), return empty list
        if not self._collection_exists:
            return []

        try:
            # Build Qdrant filter if needed
            qdrant_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )

                if conditions:
                    qdrant_filter = models.Filter(must=conditions)

            # Perform the search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=qdrant_filter
            )

            # Convert results to EmbeddingVector objects
            embeddings = []
            for result in results:
                embedding = EmbeddingVector(
                    chunk_id=result.payload.get("chunk_id", ""),
                    vector=result.vector if result.vector is not None else query_vector,  # Fallback to query vector
                    model=result.payload.get("model", ""),
                    dimensionality=result.payload.get("dimensionality", len(query_vector)),
                    metadata={k: v for k, v in result.payload.items()
                             if k not in ["chunk_id", "model", "dimensionality"]}
                )
                embeddings.append(embedding)

            return embeddings

        except Exception:
            return []

    def get_embedding_by_chunk_id(self, chunk_id: str) -> Optional[EmbeddingVector]:
        """
        Get an embedding by its chunk ID.

        Args:
            chunk_id: The chunk ID to search for

        Returns:
            The embedding vector or None if not found
        """
        # Ensure collection exists before searching
        if not self._collection_exists:
            self._ensure_collection_exists(self.vector_size)  # Use default size for initial check

        # If collection still doesn't exist (server unavailable), return None
        if not self._collection_exists:
            return None

        try:
            # Search for records with the given chunk_id
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="chunk_id",
                            match=models.MatchValue(value=chunk_id)
                        )
                    ]
                ),
                limit=1
            )

            records, _ = results  # Second value is the next_page_offset

            if not records:
                return None

            record = records[0]

            return EmbeddingVector(
                chunk_id=record.payload.get("chunk_id", ""),
                vector=record.vector,
                model=record.payload.get("model", ""),
                dimensionality=record.payload.get("dimensionality", len(record.vector) if record.vector else 0),
                metadata={k: v for k, v in record.payload.items()
                         if k not in ["chunk_id", "model", "dimensionality"]}
            )
        except Exception:
            return None

    def load_all_embeddings(self) -> List[EmbeddingVector]:
        """
        Load all embedding vectors from Qdrant storage.

        Returns:
            List of all embedding vectors in storage
        """
        # Ensure collection exists before loading
        if not self._collection_exists:
            self._ensure_collection_exists(self.vector_size)  # Use default size for initial check

        # If collection still doesn't exist (server unavailable), return empty list
        if not self._collection_exists:
            return []

        try:
            # Get all records from the collection
            # Note: For large collections, you might want to use pagination
            records, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000  # Adjust as needed, or implement pagination
            )

            embeddings = []
            for record in records:
                embedding = EmbeddingVector(
                    chunk_id=record.payload.get("chunk_id", ""),
                    vector=record.vector,
                    model=record.payload.get("model", ""),
                    dimensionality=record.payload.get("dimensionality", len(record.vector) if record.vector else 0),
                    metadata={k: v for k, v in record.payload.items()
                             if k not in ["chunk_id", "model", "dimensionality"]}
                )
                embeddings.append(embedding)

            return embeddings
        except Exception:
            return []

    def delete_embedding(self, point_id: str) -> bool:
        """
        Delete an embedding from Qdrant.

        Args:
            point_id: The ID of the point to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        # Ensure collection exists before attempting deletion
        if not self._collection_exists:
            self._ensure_collection_exists(self.vector_size)  # Use default size for initial check

        # If collection still doesn't exist (server unavailable), return False
        if not self._collection_exists:
            return False

        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )
            return True
        except Exception:
            return False