from typing import Optional


class CohereEmbeddingError(Exception):
    """Base exception for Cohere embedding related errors."""
    pass


class CohereAPIError(CohereEmbeddingError):
    """Exception raised when Cohere API returns an error."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class ContentTooLongError(CohereEmbeddingError):
    """Exception raised when content exceeds Cohere's token limit."""
    def __init__(self, token_count: int, max_tokens: int):
        self.token_count = token_count
        self.max_tokens = max_tokens
        super().__init__(f"Content has {token_count} tokens, exceeding the maximum of {max_tokens}")


class EmbeddingGenerationError(CohereEmbeddingError):
    """Exception raised when embedding generation fails."""
    pass


class RateLimitExceededError(CohereEmbeddingError):
    """Exception raised when API rate limits are exceeded."""
    pass