"""
Qdrant-specific retrieval implementation
"""
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchRequest, Filter, FieldCondition, MatchValue
from ..models.content_models import RetrievedContent
from ..config import RetrievalConfig
import logging


class QdrantRetriever:
    """
    Qdrant-specific implementation for content retrieval
    """

    def __init__(self):
        """
        Initialize Qdrant client and configuration
        """
        self.config = RetrievalConfig()
        self.client = QdrantClient(
            url=self.config.QDRANT_URL,
            api_key=self.config.QDRANT_API_KEY,
            timeout=self.config.RETRIEVAL_TIMEOUT
        )
        self.collection_name = self.config.QDRANT_COLLECTION_NAME
        self.logger = logging.getLogger(__name__)

    async def search(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedContent]:
        """
        Search for relevant content in Qdrant based on query text

        Args:
            query_text: The text to search for
            top_k: Number of top results to return
            filters: Optional filters to apply to the search

        Returns:
            List of RetrievedContent objects
        """
        try:
            # First, we need to embed the query text using the same model used for the stored content
            # Use the embedding utility adapted from rag_agent.py reference file
            from src.utils.embedding_utils import get_embedding

            query_embedding = get_embedding(query_text)

            # Build the search filter
            search_filter = self._build_filter(filters)

            # Create the search request
            search_request = SearchRequest(
                vector=query_embedding,
                limit=top_k,
                filter=search_filter,
                with_payload=True,
                with_vectors=False
            )

            # Execute the search
            search_results = self.client.search(
                collection_name=self.collection_name,
                request=search_request
            )

            # Convert search results to RetrievedContent objects
            retrieved_contents = []
            for result in search_results:
                payload = result.payload

                # Ensure we have all required fields
                content_text = payload.get("content", "")
                source_file = payload.get("source_file", "")
                source_location = payload.get("source_location", "")

                # Only include results that have the required content
                if content_text and source_file and source_location:
                    retrieved_content = RetrievedContent(
                        id=str(result.id),
                        chunk_id=str(result.id),
                        content=content_text,
                        source_file=source_file,
                        source_location=source_location,
                        relevance_score=float(result.score),
                        metadata=payload.get("metadata", {}),
                        embedding_vector=None  # We don't include the vector in the response for efficiency
                    )

                    retrieved_contents.append(retrieved_content)

            return retrieved_contents

        except Exception as e:
            self.logger.error(f"Error during Qdrant search: {str(e)}")
            raise

    def _build_filter(self, filters: Optional[Dict[str, Any]]) -> Optional[Filter]:
        """
        Build a Qdrant filter from the provided filters dictionary

        Args:
            filters: Dictionary of filters to apply

        Returns:
            Qdrant Filter object or None
        """
        if not filters:
            return None

        conditions = []

        # Add source file filter if specified
        if "source_file" in filters:
            conditions.append(
                FieldCondition(
                    key="source_file",
                    match=MatchValue(value=filters["source_file"])
                )
            )

        # Add other filters as needed
        # For now, we just handle source_file, but could extend to other fields

        if conditions:
            return Filter(must=conditions)

        return None