from fastapi import HTTPException, status
from typing import Optional


class BookContentNotFoundError(HTTPException):
    """Exception raised when requested book content is not found."""
    def __init__(self, detail: str = "Book content not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InvalidChapterError(HTTPException):
    """Exception raised when an invalid chapter is specified."""
    def __init__(self, detail: str = "Invalid chapter specified"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidSectionError(HTTPException):
    """Exception raised when an invalid section is specified."""
    def __init__(self, detail: str = "Invalid section specified"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConfigurationError(Exception):
    """Exception raised when there's an issue with application configuration."""
    def __init__(self, detail: str = "Configuration error"):
        self.detail = detail
        super().__init__(detail)


class HealthCheckError(Exception):
    """Exception raised when a health check fails."""
    def __init__(self, detail: str = "Health check failed"):
        self.detail = detail
        super().__init__(detail)