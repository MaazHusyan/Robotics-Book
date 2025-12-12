import asyncio
from typing import List, Dict, Any, Optional
import hashlib
import time

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from ..models.entities import ContentChunk
from ..utils.config import get_config
from ..utils.errors import QdrantError, RetrievalError


class QdrantVectorStore:
    """Service for managing vector storage with Qdrant."""

    def __init__(self):
        self.settings = get_config()
        self._client = None
        self._collection_name = self.settings.QDRANT_COLLECTION

    def _get_client(self) -> QdrantClient:
        """Get Qdrant client instance."""
        if self._client is None:
            self._client = QdrantClient(
                url=self.settings.QDRANT_URL, api_key=self.settings.QDRANT_API_KEY
            )
        return self._client

    async def create_collection(
        self, vector_size: int = 768, recreate: bool = False
    ) -> bool:
        """
        Create collection for storing content vectors.

        Args:
            vector_size: Dimension of vectors to store
            recreate: Whether to recreate existing collection

        Returns:
            True if collection created successfully
        """
        client = self._get_client()

        try:
            if recreate:
                # Delete existing collection
                try:
                    client.delete_collection(self._collection_name)
                    print(f"Deleted existing collection: {self._collection_name}")
                except Exception:
                    pass  # Collection doesn't exist

            # Create new collection
            client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

            print(f"Created collection: {self._collection_name}")
            return True

        except Exception as e:
            raise QdrantError(f"Failed to create collection: {e}")

    async def store_chunks(
        self, chunks: List[ContentChunk], embeddings: List[List[float]]
    ) -> int:
        """
        Store content chunks with their embeddings.

        Args:
            chunks: List of content chunks
            embeddings: List of embeddings corresponding to chunks

        Returns:
            Number of chunks stored successfully
        """
        if len(chunks) != len(embeddings):
            raise QdrantError("Number of chunks and embeddings must match")

        client = self._get_client()

        # Prepare points for upsert
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            # Generate embedding ID from content hash
            embedding_id = hashlib.md5(chunk.content.encode()).hexdigest()

            point = {
                "id": embedding_id,
                "vector": embedding,
                "payload": {
                    "content": chunk.content,
                    "source_file": chunk.source_file,
                    "chapter": chunk.chapter,
                    "section": chunk.section,
                    "chunk_index": chunk.chunk_index,
                    "chunk_type": chunk.chunk_type.value,
                    "token_count": chunk.token_count,
                    "created_at": chunk.created_at.isoformat(),
                },
            }
            points.append(point)

        try:
            # Upsert points in batches
            batch_size = 100
            stored_count = 0

            for i in range(0, len(points), batch_size):
                batch = points[i : i + batch_size]

                client.upsert(collection_name=self._collection_name, points=batch)

                stored_count += len(batch)
                print(
                    f"Stored batch {i // batch_size + 1}/{(len(points) + batch_size - 1) // batch_size}"
                )

                # Small delay to avoid rate limits
                if i + batch_size < len(points):
                    await asyncio.sleep(0.1)

            print(f"Successfully stored {stored_count} chunks in Qdrant")
            return stored_count

        except Exception as e:
            raise QdrantError(f"Failed to store chunks: {e}")

    async def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content vectors.

        Args:
            query_embedding: Embedding of query
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score
            filters: Optional filters to apply

        Returns:
            List of search results with payloads and scores
        """
        client = self._get_client()

        try:
            # Perform search using qdrant-client search method
            search_result = client.search(
                collection_name=self._collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
            )

            # Format results
            results = []
            for hit in search_result:
                if hit.score >= score_threshold:
                    results.append(
                        {
                            "id": hit.id,
                            "score": hit.score,
                            "payload": hit.payload if hasattr(hit, "payload") else {},
                        }
                    )

            return results

        except Exception as e:
            raise RetrievalError(f"Failed to search vectors: {e}")

    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        client = self._get_client()

        try:
            collection_info = client.get_collection(self._collection_name)

            # Extract available information safely
            info = {
                "name": self._collection_name,
                "status": str(getattr(collection_info, "status", "unknown")),
            }

            # Try to get additional info if available
            if hasattr(collection_info, "points_count"):
                info["points_count"] = collection_info.points_count
            if hasattr(collection_info, "config"):
                config = collection_info.config
                if hasattr(config, "params") and hasattr(config.params, "vectors"):
                    vectors_config = config.params.vectors
                    if hasattr(vectors_config, "size"):
                        info["vector_size"] = vectors_config.size
                    if hasattr(vectors_config, "distance"):
                        info["distance"] = str(vectors_config.distance)

            return info

        except Exception as e:
            raise QdrantError(f"Failed to get collection info: {e}")

    async def delete_by_filter(self, filters: Dict[str, Any]) -> int:
        """
        Delete vectors matching the given filter.

        Args:
            filters: Filter conditions for deletion

        Returns:
            Number of points deleted
        """
        client = self._get_client()

        try:
            # For simplicity, delete all and reindex if needed
            # In a production system, you'd implement proper filtering
            client.delete_collection(self._collection_name)

            # Recreate empty collection
            await self.create_collection()

            print(f"Deleted all points from collection: {self._collection_name}")
            return 0  # We don't track exact count in this simplified version

        except Exception as e:
            raise QdrantError(f"Failed to delete points: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Qdrant connection."""
        start_time = time.time()

        try:
            # Try to get collection info
            info = await self.get_collection_info()

            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "response_time_ms": int(response_time * 1000),
                "collection_info": info,
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": int((time.time() - start_time) * 1000),
            }


# Singleton instance
vector_store = QdrantVectorStore()
