import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class RAGError(Exception):
    """Base exception for RAG chatbot errors"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class DatabaseError(RAGError):
    """Database related errors"""

    pass


class QdrantError(RAGError):
    """Qdrant vector database errors"""

    pass


class AIServiceError(RAGError):
    """AI service integration errors"""

    pass


class ValidationError(RAGError):
    """Input validation errors"""

    pass


class RateLimitError(RAGError):
    """Rate limiting errors"""

    pass


class RetrievalError(RAGError):
    """Content retrieval errors"""

    pass


class CacheError(RAGError):
    """Caching system errors"""

    pass


class IngestionError(RAGError):
    """Content ingestion errors"""

    pass


def handle_error(
    error: Exception, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convert exceptions to standardized error responses"""
    if isinstance(error, DatabaseError):
        return {
            "error": "database_error",
            "message": str(error),
            "error_code": "DB_ERROR",
            "context": context,
        }
    elif isinstance(error, QdrantError):
        return {
            "error": "vector_db_error",
            "message": str(error),
            "error_code": "QDRANT_ERROR",
            "context": context,
        }
    elif isinstance(error, AIServiceError):
        return {
            "error": "ai_service_error",
            "message": str(error),
            "error_code": "AI_ERROR",
            "context": context,
        }
    elif isinstance(error, ValidationError):
        return {
            "error": "validation_error",
            "message": str(error),
            "error_code": "VALIDATION_ERROR",
            "context": context,
        }
    elif isinstance(error, RateLimitError):
        return {
            "error": "rate_limit_error",
            "message": str(error),
            "error_code": "RATE_LIMIT",
            "context": context,
        }
    else:
        return {
            "error": "internal_error",
            "message": str(error),
            "error_code": "INTERNAL_ERROR",
            "context": context,
        }


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log error with context"""
    error_response = handle_error(error, context)
    logger.error(f"Error occurred: {error_response}")
