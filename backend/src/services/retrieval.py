import asyncio
from typing import List, Dict, Any, Optional
import time

from ..services.embeddings import embedding_service
from ..services.vector_store import vector_store
from ..utils.config import get_config
from ..utils.errors import RetrievalError, AIServiceError


class ContentRetrievalService:
    """Service for retrieving relevant content based on user queries."""

    def __init__(self):
        self.settings = get_config()
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def retrieve_relevant_content(
        self,
        query: str,
        context_chunks: Optional[List[str]] = None,
        max_results: int = 5,
        min_score: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Retrieve relevant content for a given query.

        Args:
            query: User's question or search term
            context_chunks: Optional highlighted text chunks for additional context
            max_results: Maximum number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            Dictionary with retrieved content and metadata
        """
        if not query or not query.strip():
            raise RetrievalError("Query cannot be empty")

        start_time = time.time()

        try:
            # Generate embedding for query
            query_embedding = await self.embedding_service.generate_embedding(
                query.strip()
            )

            # Search for similar content
            search_results = await self.vector_store.search_similar(
                query_embedding=query_embedding,
                limit=max_results,
                score_threshold=min_score,
            )

            # Add context chunks if provided
            if context_chunks:
                context_text = "\n\n".join(context_chunks)
                context_embedding = await self.embedding_service.generate_embedding(
                    context_text
                )

                # Search for content similar to context
                context_results = await self.vector_store.search_similar(
                    query_embedding=context_embedding,
                    limit=max_results // 2,
                    score_threshold=min_score,
                )

                # Merge results, prioritizing query results
                all_results = search_results.copy()
                for context_result in context_results:
                    # Add if not already present
                    if not any(r["id"] == context_result["id"] for r in all_results):
                        all_results.append(context_result)

                # Sort by score and limit
                all_results.sort(key=lambda x: x["score"], reverse=True)
                search_results = all_results[:max_results]

            # Format results for consumption
            formatted_results = []
            sources = set()

            for result in search_results:
                payload = result.get("payload", {})

                formatted_result = {
                    "content": payload.get("content", ""),
                    "source_file": payload.get("source_file", ""),
                    "chapter": payload.get("chapter", ""),
                    "section": payload.get("section", ""),
                    "chunk_index": payload.get("chunk_index", 0),
                    "chunk_type": payload.get("chunk_type", "paragraph"),
                    "score": result.get("score", 0.0),
                    "token_count": payload.get("token_count", 0),
                }

                formatted_results.append(formatted_result)
                sources.add(payload.get("source_file", ""))

            response_time = time.time() - start_time

            return {
                "query": query,
                "results": formatted_results,
                "sources": list(sources),
                "total_results": len(formatted_results),
                "response_time_ms": int(response_time * 1000),
                "context_provided": bool(context_chunks),
                "context_chunks_count": len(context_chunks) if context_chunks else 0,
            }

        except AIServiceError as e:
            raise RetrievalError(f"Failed to generate query embedding: {e}")
        except Exception as e:
            raise RetrievalError(f"Failed to retrieve content: {e}")

    async def get_content_by_source(
        self, source_file: str, chapter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all content chunks from a specific source file.

        Args:
            source_file: Path to source file
            chapter: Optional chapter filter

        Returns:
            List of content chunks
        """
        try:
            # Build filters
            filters = {"source_file": source_file}
            if chapter:
                filters["chapter"] = chapter

            # Search with a dummy embedding to get all matching content
            # This is a workaround for Qdrant not having a simple "get by filter" method
            dummy_embedding = [0.0] * 768  # 768 is our embedding dimension

            search_results = await self.vector_store.search_similar(
                query_embedding=dummy_embedding,
                limit=100,  # Get many results
                score_threshold=0.0,  # No score filtering
                filters=filters,
            )

            # Format results
            formatted_results = []
            for result in search_results:
                payload = result.get("payload", {})
                formatted_results.append(
                    {
                        "content": payload.get("content", ""),
                        "source_file": payload.get("source_file", ""),
                        "chapter": payload.get("chapter", ""),
                        "section": payload.get("section", ""),
                        "chunk_index": payload.get("chunk_index", 0),
                        "chunk_type": payload.get("chunk_type", "paragraph"),
                        "token_count": payload.get("token_count", 0),
                    }
                )

            # Sort by chunk_index to maintain order
            formatted_results.sort(key=lambda x: x["chunk_index"])

            return formatted_results

        except Exception as e:
            raise RetrievalError(f"Failed to get content by source: {e}")

    async def get_chapter_overview(self, chapter: str) -> Dict[str, Any]:
        """
        Get overview of content in a specific chapter.

        Args:
            chapter: Chapter name

        Returns:
            Dictionary with chapter information
        """
        try:
            # Get all content from chapter
            dummy_embedding = [0.0] * 768

            search_results = await self.vector_store.search_similar(
                query_embedding=dummy_embedding,
                limit=200,  # Get many results
                score_threshold=0.0,
                filters={"chapter": chapter},
            )

            if not search_results:
                return {
                    "chapter": chapter,
                    "sections": [],
                    "total_chunks": 0,
                    "total_tokens": 0,
                }

            # Analyze chapter content
            sections = {}
            total_chunks = len(search_results)
            total_tokens = 0

            for result in search_results:
                payload = result.get("payload", {})
                section = payload.get("section", "unknown")
                chunk_type = payload.get("chunk_type", "paragraph")
                token_count = payload.get("token_count", 0)

                if section not in sections:
                    sections[section] = {
                        "chunk_count": 0,
                        "chunk_types": {},
                        "total_tokens": 0,
                    }

                sections[section]["chunk_count"] += 1
                sections[section]["total_tokens"] += token_count
                total_tokens += token_count

                if chunk_type not in sections[section]["chunk_types"]:
                    sections[section]["chunk_types"][chunk_type] = 0
                sections[section]["chunk_types"][chunk_type] += 1

            return {
                "chapter": chapter,
                "sections": sections,
                "total_chunks": total_chunks,
                "total_tokens": total_tokens,
            }

        except Exception as e:
            raise RetrievalError(f"Failed to get chapter overview: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on retrieval service."""
        start_time = time.time()

        try:
            # Test embedding service
            embedding_health = await self.embedding_service.health_check()

            # Test vector store
            vector_health = await self.vector_store.health_check()

            # Test simple retrieval
            test_result = await self.retrieve_relevant_content(
                query="test query", max_results=1, min_score=0.1
            )

            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "response_time_ms": int(response_time * 1000),
                "embedding_service": embedding_health,
                "vector_store": vector_health,
                "test_retrieval": {
                    "results_count": len(test_result.get("results", [])),
                    "response_time_ms": test_result.get("response_time_ms", 0),
                },
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": int((time.time() - start_time) * 1000),
            }


# Singleton instance
retrieval_service = ContentRetrievalService()
