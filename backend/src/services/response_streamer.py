import asyncio
from typing import Dict, Any, AsyncGenerator
import time
import json

from ..utils.errors import AIServiceError


class ResponseStreamer:
    """Service for streaming responses in real-time."""

    def __init__(self):
        self.active_streams: Dict[str, Dict[str, Any]] = {}

    async def create_stream(
        self,
        query_id: str,
        content_generator: AsyncGenerator[str, None],
        sources: list = None,
        metadata: Dict[str, Any] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Create a response stream for real-time delivery.

        Args:
            query_id: Unique identifier for the query
            content_generator: Async generator yielding content chunks
            sources: List of sources used in response
            metadata: Additional metadata

        Yields:
            Stream messages for WebSocket delivery
        """
        start_time = time.time()

        # Register stream
        self.active_streams[query_id] = {
            "start_time": start_time,
            "sources": sources or [],
            "metadata": metadata or {},
            "total_chars": 0,
            "chunks_sent": 0,
        }

        try:
            # Send start event
            yield {
                "type": "response_start",
                "data": {
                    "query_id": query_id,
                    "sources": sources or [],
                    "estimated_duration": metadata.get("estimated_duration", 1500)
                    if metadata
                    else 1500,
                },
                "timestamp": time.time(),
            }

            # Stream content
            full_response = ""
            async for chunk in content_generator:
                if chunk:
                    full_response += chunk
                    self.active_streams[query_id]["total_chars"] += len(chunk)
                    self.active_streams[query_id]["chunks_sent"] += 1

                    yield {
                        "type": "response_chunk",
                        "data": {
                            "query_id": query_id,
                            "content": chunk,
                            "is_complete": False,
                            "chunk_index": self.active_streams[query_id]["chunks_sent"],
                        },
                        "timestamp": time.time(),
                    }

                    # Small delay for natural streaming effect
                    await asyncio.sleep(0.05)

            # Send end event
            end_time = time.time()
            response_time = int((end_time - start_time) * 1000)

            yield {
                "type": "response_end",
                "data": {
                    "query_id": query_id,
                    "response_time_ms": response_time,
                    "total_chars": self.active_streams[query_id]["total_chars"],
                    "total_chunks": self.active_streams[query_id]["chunks_sent"],
                    "sources_used": len(sources or []),
                    "words_estimated": len(full_response.split()),
                },
                "timestamp": time.time(),
            }

        except Exception as e:
            yield {
                "type": "error",
                "data": {
                    "query_id": query_id,
                    "error": str(e),
                    "error_type": "streaming_error",
                },
                "timestamp": time.time(),
            }
        finally:
            # Clean up stream
            if query_id in self.active_streams:
                del self.active_streams[query_id]

    async def stream_text_response(
        self,
        query_id: str,
        text: str,
        sources: list = None,
        chunk_size: int = 10,
        delay: float = 0.1,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a text response with natural chunking.

        Args:
            query_id: Unique identifier for the query
            text: Complete response text
            sources: List of sources used
            chunk_size: Number of words per chunk
            delay: Delay between chunks in seconds

        Yields:
            Stream messages
        """

        async def text_generator():
            words = text.split()

            for i in range(0, len(words), chunk_size):
                chunk_words = words[i : i + chunk_size]
                chunk = " ".join(chunk_words)
                yield chunk

                if i + chunk_size < len(words):
                    await asyncio.sleep(delay)

        async for message in self.create_stream(
            query_id=query_id,
            content_generator=text_generator(),
            sources=sources,
            metadata={"chunking_method": "word_based"},
        ):
            yield message

    async def stream_json_response(
        self, query_id: str, response_data: Dict[str, Any], sources: list = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a structured JSON response.

        Args:
            query_id: Unique identifier for the query
            response_data: Structured response data
            sources: List of sources used

        Yields:
            Stream messages
        """
        # Convert structured response to text for streaming
        if "explanation" in response_data:
            text = response_data["explanation"]
        elif "answer" in response_data:
            text = response_data["answer"]
        else:
            text = json.dumps(response_data, indent=2)

        async for message in self.stream_text_response(
            query_id=query_id, text=text, sources=sources
        ):
            yield message

    def get_stream_stats(self, query_id: str) -> Dict[str, Any]:
        """Get statistics for an active stream."""
        if query_id not in self.active_streams:
            return {"error": "Stream not found"}

        stream_info = self.active_streams[query_id]
        current_time = time.time()
        elapsed_time = current_time - stream_info["start_time"]

        return {
            "query_id": query_id,
            "elapsed_time_ms": int(elapsed_time * 1000),
            "total_chars": stream_info["total_chars"],
            "chunks_sent": stream_info["chunks_sent"],
            "average_chunk_size": stream_info["total_chars"]
            / max(1, stream_info["chunks_sent"]),
            "sources_count": len(stream_info["sources"]),
            "is_active": True,
        }

    def get_all_streams_stats(self) -> Dict[str, Any]:
        """Get statistics for all active streams."""
        return {
            "active_streams": len(self.active_streams),
            "stream_ids": list(self.active_streams.keys()),
            "streams": {
                query_id: self.get_stream_stats(query_id)
                for query_id in self.active_streams.keys()
            },
        }

    async def cancel_stream(self, query_id: str) -> bool:
        """
        Cancel an active stream.

        Args:
            query_id: Stream identifier to cancel

        Returns:
            True if stream was cancelled, False if not found
        """
        if query_id in self.active_streams:
            # Send cancellation event
            yield {
                "type": "stream_cancelled",
                "data": {"query_id": query_id, "reason": "user_cancelled"},
                "timestamp": time.time(),
            }

            # Clean up
            del self.active_streams[query_id]
            return True

        return False

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on streaming service."""
        return {
            "status": "healthy",
            "active_streams": len(self.active_streams),
            "supported_formats": ["text", "json", "structured"],
            "default_chunk_size": 10,
            "default_delay": 0.1,
        }


# Singleton instance
response_streamer = ResponseStreamer()
