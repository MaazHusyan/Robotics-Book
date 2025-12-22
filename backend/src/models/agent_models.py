"""
Agent-specific data models for the chatbot agent integration.

Based on the data-model.md specification for the 001-chatbot-agent-integration feature.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class ChatSession(BaseModel):
    """
    Represents a conversation session between user and agent.
    """
    session_id: str = str(uuid.uuid4())
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = []  # List of {role: "user|assistant", content: str, timestamp: datetime}
    metadata: Dict[str, Any] = {}


class AgentConfig(BaseModel):
    """
    Configuration for the agent behavior.
    """
    model_name: str = "gemini-2.5-flash"  # Default model
    temperature: float = 0.7
    max_tokens: int = 1000
    top_k: int = 5  # Number of results to retrieve
    min_relevance_score: float = 0.5
    enable_tracing: bool = False
    timeout_seconds: int = 30
    fallback_response: str = "I couldn't find relevant information to answer your question. Please try rephrasing or ask about a different topic related to robotics."


class AgentToolResult(BaseModel):
    """
    Result from agent tools (like retrieval).
    """
    tool_name: str
    success: bool
    content: List[Dict[str, Any]] = []  # Using generic dict for flexibility with RetrievedContent
    error: Optional[str] = None
    execution_time: Optional[float] = None


class AgentResponse(BaseModel):
    """
    Response from the agent with source attribution.
    """
    session_id: str
    query: str
    response: str
    sources: List[Dict[str, Any]] = []  # Using generic dict for flexibility with RetrievedContent
    conversation_turn: int
    timestamp: datetime = datetime.now()
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None  # Processing time in seconds
    has_relevant_content: bool = True
    error: Optional[str] = None


class AgentQuery(BaseModel):
    """
    Query with agent-specific context and options.
    """
    query_text: str
    session_id: Optional[str] = None
    agent_instructions: Optional[str] = "You are a robotics expert assistant. Answer questions based on the provided context from robotics books. Always cite your sources."
    require_sources: bool = True
    max_tokens: Optional[int] = 1000
    temperature: float = 0.7
    conversation_context: Optional[Dict[str, Any]] = None  # Using dict for flexibility


class ChatRequest(BaseModel):
    """
    Request model for chat interactions.
    """
    message: str
    session_id: Optional[str] = None  # If not provided, creates new session
    require_sources: bool = True
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class ChatResponse(BaseModel):
    """
    Response model for chat interactions.
    """
    session_id: str
    response: str
    sources: List[Dict[str, Any]]  # Using generic dict for flexibility with RetrievedContent
    conversation_turn: int
    has_relevant_content: bool
    timestamp: datetime = datetime.now()