import asyncio
from typing import Dict, Any, List, Optional
import time
import uuid

from ..utils.errors import ValidationError, RetrievalError


class ContextManager:
    """Service for managing highlighted text context in RAG queries."""

    def __init__(self):
        self.active_contexts: Dict[str, Dict[str, Any]] = {}
        self.context_ttl = 1800  # 30 minutes in seconds

    async def add_context(
        self,
        session_id: str,
        context_chunks: List[str],
        metadata: Dict[str, Any] = None,
    ) -> str:
        """
        Add context chunks for a session.

        Args:
            session_id: Session identifier
            context_chunks: List of highlighted text chunks
            metadata: Additional context metadata

        Returns:
            Context ID for reference
        """
        if not context_chunks:
            raise ValidationError("Context chunks cannot be empty")

        if len(context_chunks) > 5:
            raise ValidationError("Too many context chunks (max 5)")

        context_id = str(uuid.uuid4())

        # Validate and clean context chunks
        validated_chunks = []
        for i, chunk in enumerate(context_chunks):
            if not chunk or not chunk.strip():
                continue

            cleaned_chunk = chunk.strip()
            if len(cleaned_chunk) < 10:
                continue  # Skip very short chunks

            validated_chunks.append(
                {
                    "text": cleaned_chunk,
                    "index": i,
                    "length": len(cleaned_chunk),
                    "word_count": len(cleaned_chunk.split()),
                }
            )

        if not validated_chunks:
            raise ValidationError("No valid context chunks provided")

        # Store context
        context_data = {
            "context_id": context_id,
            "session_id": session_id,
            "chunks": validated_chunks,
            "metadata": metadata or {},
            "created_at": time.time(),
            "last_used": time.time(),
            "usage_count": 0,
        }

        self.active_contexts[context_id] = context_data

        return context_id

    async def get_context(self, context_id: str) -> Dict[str, Any]:
        """
        Retrieve context by ID.

        Args:
            context_id: Context identifier

        Returns:
            Context data or None if not found
        """
        context = self.active_contexts.get(context_id)

        if not context:
            return {"error": "Context not found"}

        # Check if context has expired
        if time.time() - context["created_at"] > self.context_ttl:
            await self.remove_context(context_id)
            return {"error": "Context expired"}

        # Update usage
        context["last_used"] = time.time()
        context["usage_count"] += 1

        return context

    async def update_context(
        self,
        context_id: str,
        additional_chunks: List[str] = None,
        metadata_update: Dict[str, Any] = None,
    ) -> bool:
        """
        Update existing context.

        Args:
            context_id: Context identifier
            additional_chunks: Additional chunks to add
            metadata_update: Metadata to update

        Returns:
            True if updated successfully, False otherwise
        """
        context = self.active_contexts.get(context_id)

        if not context:
            return False

        # Add additional chunks
        if additional_chunks:
            current_chunk_count = len(context["chunks"])

            for chunk in additional_chunks:
                if not chunk or not chunk.strip():
                    continue

                if len(context["chunks"]) >= 5:
                    break  # Max chunks reached

                cleaned_chunk = chunk.strip()
                context["chunks"].append(
                    {
                        "text": cleaned_chunk,
                        "index": current_chunk_count + len(context["chunks"]) - 5,
                        "length": len(cleaned_chunk),
                        "word_count": len(cleaned_chunk.split()),
                    }
                )

        # Update metadata
        if metadata_update:
            context["metadata"].update(metadata_update)

        context["last_used"] = time.time()

        return True

    async def remove_context(self, context_id: str) -> bool:
        """
        Remove context by ID.

        Args:
            context_id: Context identifier

        Returns:
            True if removed, False if not found
        """
        if context_id in self.active_contexts:
            del self.active_contexts[context_id]
            return True

        return False

    async def clear_session_contexts(self, session_id: str) -> int:
        """
        Clear all contexts for a session.

        Args:
            session_id: Session identifier

        Returns:
            Number of contexts cleared
        """
        to_remove = [
            context_id
            for context_id, context in self.active_contexts.items()
            if context.get("session_id") == session_id
        ]

        for context_id in to_remove:
            del self.active_contexts[context_id]

        return len(to_remove)

    async def get_session_contexts(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all contexts for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of context data
        """
        session_contexts = [
            context
            for context in self.active_contexts.values()
            if context.get("session_id") == session_id
        ]

        # Sort by last used time
        session_contexts.sort(key=lambda x: x.get("last_used", 0), reverse=True)

        return session_contexts

    def format_context_for_query(self, context_data: Dict[str, Any]) -> str:
        """
        Format context data for inclusion in RAG queries.

        Args:
            context_data: Context data from get_context()

        Returns:
            Formatted context string
        """
        if "error" in context_data:
            return ""

        chunks = context_data.get("chunks", [])

        if not chunks:
            return ""

        formatted_parts = []

        for chunk in chunks:
            chunk_text = chunk.get("text", "")
            chunk_index = chunk.get("index", 0)

            formatted_parts.append(
                f"[Highlighted Context {chunk_index + 1}]:\n{chunk_text}"
            )

        return "\n\n".join(formatted_parts)

    async def merge_contexts(
        self, context_ids: List[str], session_id: str = None
    ) -> Dict[str, Any]:
        """
        Merge multiple contexts into one.

        Args:
            context_ids: List of context IDs to merge
            session_id: Optional session ID for validation

        Returns:
            Merged context data
        """
        if not context_ids:
            return {"error": "No context IDs provided"}

        merged_chunks = []
        all_metadata = {}
        total_length = 0
        total_word_count = 0

        for context_id in context_ids:
            context = await self.get_context(context_id)

            if "error" in context:
                continue  # Skip invalid contexts

            # Validate session if provided
            if session_id and context.get("session_id") != session_id:
                continue  # Skip contexts from other sessions

            chunks = context.get("chunks", [])
            metadata = context.get("metadata", {})

            # Add chunks (up to limit)
            for chunk in chunks:
                if len(merged_chunks) >= 5:
                    break  # Max chunks reached

                merged_chunks.append({**chunk, "source_context_id": context_id})

            # Merge metadata
            all_metadata.update(metadata)
            total_length += context.get("total_length", 0)
            total_word_count += sum(chunk.get("word_count", 0) for chunk in chunks)

        if not merged_chunks:
            return {"error": "No valid contexts to merge"}

        return {
            "context_id": str(uuid.uuid4()),  # New merged context ID
            "session_id": session_id,
            "chunks": merged_chunks,
            "metadata": all_metadata,
            "source_context_ids": context_ids,
            "total_length": total_length,
            "total_word_count": total_word_count,
            "chunk_count": len(merged_chunks),
            "created_at": time.time(),
            "merged": True,
        }

    async def cleanup_expired_contexts(self) -> int:
        """
        Clean up expired contexts.

        Returns:
            Number of contexts cleaned up
        """
        current_time = time.time()
        expired_contexts = [
            context_id
            for context_id, context in self.active_contexts.items()
            if current_time - context.get("created_at", 0) > self.context_ttl
        ]

        for context_id in expired_contexts:
            del self.active_contexts[context_id]

        return len(expired_contexts)

    def get_context_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about active contexts.

        Returns:
            Context statistics
        """
        if not self.active_contexts:
            return {
                "total_contexts": 0,
                "total_sessions": 0,
                "average_chunks_per_context": 0,
                "total_words": 0,
                "oldest_context_age": 0,
                "newest_context_age": 0,
            }

        total_contexts = len(self.active_contexts)
        total_chunks = sum(
            len(context.get("chunks", [])) for context in self.active_contexts.values()
        )
        total_words = sum(
            sum(chunk.get("word_count", 0) for chunk in context.get("chunks", []))
            for context in self.active_contexts.values()
        )

        sessions = set(
            context.get("session_id") for context in self.active_contexts.values()
        )

        current_time = time.time()
        context_ages = [
            current_time - context.get("created_at", 0)
            for context in self.active_contexts.values()
        ]

        return {
            "total_contexts": total_contexts,
            "total_sessions": len(sessions),
            "average_chunks_per_context": total_chunks / total_contexts
            if total_contexts > 0
            else 0,
            "total_words": total_words,
            "oldest_context_age": min(context_ages) if context_ages else 0,
            "newest_context_age": max(context_ages) if context_ages else 0,
            "context_ttl": self.context_ttl,
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on context manager.

        Returns:
            Health check result
        """
        try:
            # Test context creation
            test_context_id = await self.add_context(
                session_id="health_check",
                context_chunks=["Test context for health check"],
                metadata={"test": True},
            )

            # Test context retrieval
            retrieved_context = await self.get_context(test_context_id)

            # Test context removal
            removed = await self.remove_context(test_context_id)

            # Clean up test data
            await self.clear_session_contexts("health_check")

            stats = self.get_context_statistics()

            return {
                "status": "healthy",
                "test_operations": {
                    "create_context": "success" if test_context_id else "failed",
                    "retrieve_context": "success"
                    if "error" not in retrieved_context
                    else "failed",
                    "remove_context": "success" if removed else "failed",
                },
                "statistics": stats,
                "context_ttl": self.context_ttl,
            }

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Singleton instance
context_manager = ContextManager()
