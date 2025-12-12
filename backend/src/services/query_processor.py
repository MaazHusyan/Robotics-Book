import asyncio
from typing import Dict, Any, Optional
import time
import uuid

from ..services.retrieval import retrieval_service
from ..services.rag_agent import rag_agent_service
from ..utils.errors import ValidationError, AIServiceError


class QueryProcessor:
    """Service for processing and validating user queries."""

    def __init__(self):
        self.retrieval_service = retrieval_service
        self.rag_agent_service = rag_agent_service

    async def process_query(
        self,
        question: str,
        context_chunks: Optional[list] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a user query through the complete pipeline.

        Args:
            question: User's question
            context_chunks: Optional highlighted text chunks
            session_id: Optional session identifier

        Returns:
            Dictionary with processed query and metadata
        """
        # Validate input
        self._validate_query(question)

        start_time = time.time()
        query_id = str(uuid.uuid4())

        try:
            # Preprocess query
            processed_question = self._preprocess_question(question)

            # Determine query type
            query_type = self._classify_query(processed_question)

            # Retrieve relevant content
            retrieval_result = await self.retrieval_service.retrieve_relevant_content(
                query=processed_question,
                context_chunks=context_chunks,
                max_results=5,
                min_score=0.7,
            )

            # Process with RAG agent
            agent_result = await self.rag_agent_service.process_query(
                question=processed_question,
                context_chunks=context_chunks,
                session_id=session_id,
            )

            # Combine results
            processing_time = time.time() - start_time

            return {
                "query_id": query_id,
                "original_question": question,
                "processed_question": processed_question,
                "query_type": query_type,
                "context_chunks": context_chunks or [],
                "retrieval_result": retrieval_result,
                "agent_result": agent_result,
                "processing_time_ms": int(processing_time * 1000),
                "session_id": session_id,
                "timestamp": time.time(),
            }

        except Exception as e:
            raise AIServiceError(f"Failed to process query: {e}")

    def _validate_query(self, question: str):
        """Validate user query."""
        if not question:
            raise ValidationError("Question cannot be empty")

        question = question.strip()

        if len(question) == 0:
            raise ValidationError("Question cannot be empty")

        if len(question) > 1000:
            raise ValidationError("Question exceeds 1000 characters")

        # Check for potential injection attempts
        dangerous_patterns = [
            "<script",
            "javascript:",
            "data:",
            "vbscript:",
            "onload=",
            "onerror=",
            "onclick=",
        ]

        question_lower = question.lower()
        for pattern in dangerous_patterns:
            if pattern in question_lower:
                raise ValidationError("Question contains potentially unsafe content")

    def _preprocess_question(self, question: str) -> str:
        """Preprocess question for better retrieval."""
        # Remove extra whitespace
        question = " ".join(question.split())

        # Remove special characters that might interfere with search
        question = question.replace("\n", " ").replace("\r", " ")

        # Normalize quotes
        question = question.replace('"', "'").replace('"', "'")

        return question.strip()

    def _classify_query(self, question: str) -> str:
        """Classify the type of query."""
        question_lower = question.lower()

        # Question words
        question_words = [
            "what",
            "how",
            "why",
            "when",
            "where",
            "who",
            "which",
            "explain",
            "describe",
        ]

        # Definition words
        definition_words = ["define", "definition", "what is", "what are", "meaning"]

        # Comparison words
        comparison_words = ["compare", "difference", "versus", "vs", "better", "worse"]

        # Procedure words
        procedure_words = [
            "how to",
            "steps",
            "process",
            "method",
            "procedure",
            "algorithm",
        ]

        # Check for question type
        if any(word in question_lower for word in definition_words):
            return "definition"
        elif any(word in question_lower for word in comparison_words):
            return "comparison"
        elif any(word in question_lower for word in procedure_words):
            return "procedure"
        elif any(word in question_lower for word in question_words):
            return "question"
        else:
            return "general"

    async def get_query_suggestions(self, partial_query: str) -> list:
        """Get suggestions for partial queries."""
        # This could be enhanced with actual search suggestions
        # For now, return common robotics topics
        common_topics = [
            "kinematics",
            "dynamics",
            "actuators",
            "sensors",
            "control systems",
            "inverse kinematics",
            "forward kinematics",
            "trajectory planning",
            "balance",
            "gait planning",
        ]

        partial_lower = partial_query.lower()
        suggestions = [
            topic
            for topic in common_topics
            if partial_lower in topic or topic.startswith(partial_lower)
        ]

        return suggestions[:5]  # Limit to 5 suggestions

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on query processor."""
        start_time = time.time()

        try:
            # Test query processing
            test_result = await self.process_query(
                question="What is robotics?",
                context_chunks=None,
                session_id="health_check",
            )

            processing_time = time.time() - start_time

            return {
                "status": "healthy",
                "response_time_ms": int(processing_time * 1000),
                "test_query": {
                    "query_type": test_result.get("query_type", "unknown"),
                    "processing_time_ms": test_result.get("processing_time_ms", 0),
                    "retrieval_results": len(
                        test_result.get("retrieval_result", {}).get("results", [])
                    ),
                    "agent_response_length": len(
                        test_result.get("agent_result", {}).get("response", "")
                    ),
                },
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": int((time.time() - start_time) * 1000),
            }


# Singleton instance
query_processor = QueryProcessor()
