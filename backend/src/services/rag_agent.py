import asyncio
from typing import List, Dict, Any, Optional
import time
import uuid

from openai import OpenAI
from openai.types import Agent

from ..services.retrieval import retrieval_service
from ..utils.config import get_config
from ..utils.errors import AIServiceError, RetrievalError


class RAGAgentService:
    """Service for managing RAG agent with OpenAI Agents SDK and Gemini."""

    def __init__(self):
        self.settings = get_config()
        self.client = OpenAI(
            api_key=self.settings.GEMINI_API_KEY, base_url=self.settings.OPENAI_BASE_URL
        )
        self.retrieval_service = retrieval_service

        # System prompt for Robotics Book Tutor
        self.system_prompt = """You are a Robotics Book Tutor, an AI assistant helping students learn from Physical and Humanoid Robotics book.

Your role:
- Answer questions using ONLY the provided robotics book content
- Explain complex concepts clearly and progressively
- When students highlight text, use that as specific context
- Always cite your sources (chapter and section)
- If information isn't in the book, say so clearly
- Focus on educational value and practical understanding

Guidelines:
- Use simple language with technical terms defined
- Provide step-by-step explanations for complex topics
- Include practical examples when relevant
- Encourage further learning by suggesting related topics

Stay within the scope of the provided robotics content and maintain a helpful, educational tone."""

    def create_robotics_tutor_agent(self) -> Agent:
        """Create and configure the Robotics Book Tutor agent."""

        try:
            agent = Agent(
                name="Robotics Book Tutor",
                instructions=self.system_prompt,
                model="gemini-1.5-flash",
                tools=[self._create_search_tool()],
            )

            return agent

        except Exception as e:
            raise AIServiceError(f"Failed to create agent: {e}")

    def _create_search_tool(self):
        """Create search tool for the agent."""

        def search_robotics_content(
            query: str, context_chunks: Optional[List[str]] = None
        ) -> str:
            """Search robotics book content for relevant information.

            Args:
                query: User's question or search term
                context_chunks: Optional list of highlighted text chunks for additional context

            Returns:
                Formatted context string with relevant content chunks
            """
            # This will be called by the agent during execution
            # For now, return a placeholder that will be replaced during execution
            return f"Searching for: {query}"

        # Register as a tool
        search_robotics_content.__name__ = "search_robotics_content"
        search_robotics_content.__doc__ = (
            """Search robotics book content for relevant information."""
        )

        return search_robotics_content

    async def process_query(
        self,
        question: str,
        context_chunks: Optional[List[str]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a user query using the RAG agent.

        Args:
            question: User's question
            context_chunks: Optional highlighted text chunks
            session_id: Optional session identifier

        Returns:
            Dictionary with response and metadata
        """
        if not question or not question.strip():
            raise AIServiceError("Question cannot be empty")

        start_time = time.time()
        query_id = str(uuid.uuid4())

        try:
            # Retrieve relevant content first
            retrieval_result = await self.retrieval_service.retrieve_relevant_content(
                query=question.strip(),
                context_chunks=context_chunks,
                max_results=5,
                min_score=0.7,
            )

            # Format context for the agent
            context_text = self._format_context_for_agent(retrieval_result)

            # Create agent instance
            agent = self.create_robotics_tutor_agent()

            # Prepare messages for the agent
            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"Context:\n{context_text}\n\nQuestion: {question}",
                },
            ]

            # Generate response using client directly (simplified approach)
            response = self.client.chat.completions.create(
                model="gemini-1.5-flash",
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=1000,
            )

            # Stream response
            full_response = ""
            chunks = []

            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    chunks.append({"content": content, "timestamp": time.time()})

            response_time = time.time() - start_time

            return {
                "query_id": query_id,
                "question": question,
                "response": full_response,
                "chunks": chunks,
                "sources": retrieval_result.get("sources", []),
                "context_used": retrieval_result.get("context_provided", False),
                "retrieval_results": retrieval_result.get("results", []),
                "response_time_ms": int(response_time * 1000),
                "session_id": session_id,
                "timestamp": time.time(),
            }

        except RetrievalError as e:
            raise AIServiceError(f"Retrieval failed: {e}")
        except Exception as e:
            raise AIServiceError(f"Failed to process query: {e}")

    def _format_context_for_agent(self, retrieval_result: Dict[str, Any]) -> str:
        """Format retrieved content for agent consumption."""
        results = retrieval_result.get("results", [])

        if not results:
            return "No relevant content found in the robotics book."

        context_parts = []

        for i, result in enumerate(results, 1):
            source_file = result.get("source_file", "")
            content = result.get("content", "")
            chapter = result.get("chapter", "")
            section = result.get("section", "")
            score = result.get("score", 0.0)

            context_part = f"""Source {i}:
File: {source_file}
Chapter: {chapter}
Section: {section}
Relevance: {score:.2f}
Content: {content}"""

            context_parts.append(context_part)

        return "\n\n".join(context_parts)

    async def stream_response(
        self,
        question: str,
        context_chunks: Optional[List[str]] = None,
        session_id: Optional[str] = None,
    ):
        """
        Stream response for real-time delivery.

        Args:
            question: User's question
            context_chunks: Optional highlighted text chunks
            session_id: Optional session identifier

        Yields:
            Response chunks as they are generated
        """
        try:
            # Retrieve relevant content
            retrieval_result = await self.retrieval_service.retrieve_relevant_content(
                query=question.strip(),
                context_chunks=context_chunks,
                max_results=5,
                min_score=0.7,
            )

            # Format context
            context_text = self._format_context_for_agent(retrieval_result)

            # Prepare messages
            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"Context:\n{context_text}\n\nQuestion: {question}",
                },
            ]

            # Stream response
            response = self.client.chat.completions.create(
                model="gemini-1.5-flash",
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=1000,
            )

            query_id = str(uuid.uuid4())
            start_time = time.time()

            # Send start event
            yield {
                "type": "response_start",
                "data": {
                    "query_id": query_id,
                    "sources": retrieval_result.get("sources", []),
                    "context_used": retrieval_result.get("context_provided", False),
                },
            }

            # Stream content chunks
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield {
                        "type": "response_chunk",
                        "data": {
                            "query_id": query_id,
                            "content": chunk.choices[0].delta.content,
                            "timestamp": time.time(),
                        },
                    }

            # Send end event
            yield {
                "type": "response_end",
                "data": {
                    "query_id": query_id,
                    "response_time_ms": int((time.time() - start_time) * 1000),
                    "sources_count": len(retrieval_result.get("sources", [])),
                },
            }

        except Exception as e:
            yield {"type": "error", "data": {"error": str(e), "timestamp": time.time()}}

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on RAG agent service."""
        start_time = time.time()

        try:
            # Test retrieval service
            retrieval_health = await self.retrieval_service.health_check()

            # Test simple query
            test_result = await self.process_query(
                question="What is robotics?",
                context_chunks=None,
                session_id="health_check",
            )

            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "response_time_ms": int(response_time * 1000),
                "retrieval_service": retrieval_health,
                "test_query": {
                    "response_length": len(test_result.get("response", "")),
                    "response_time_ms": test_result.get("response_time_ms", 0),
                    "sources_found": len(test_result.get("sources", [])),
                },
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": int((time.time() - start_time) * 1000),
            }


# Singleton instance
rag_agent_service = RAGAgentService()
