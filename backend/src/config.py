from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Application settings
    ENVIRONMENT: Optional[str] = "development"
    API_HOST: Optional[str] = "0.0.0.0"
    API_PORT: Optional[int] = 8000
    DEBUG: Optional[bool] = True
    LOG_LEVEL: Optional[str] = "info"

    # Cohere Configuration
    COHERE_API_KEY: Optional[str] = None

    # Jina AI Configuration
    JINA_API_KEY: Optional[str] = None

    # Qdrant Configuration
    QDRANT_URL: Optional[str] = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: Optional[str] = "robotics_book_embeddings"

    # Embedding Configuration
    EMBEDDING_MODEL: str = "jina-embeddings-v3"
    EMBEDDING_INPUT_TYPE: str = "retrieval.query"
    EMBEDDING_TRUNCATE: str = "END"
    EMBEDDING_BATCH_SIZE: int = 32  # Jina typically supports smaller batch sizes
    EMBEDDING_RATE_LIMIT_REQUESTS: int = 200  # Higher rate limit for Jina
    EMBEDDING_RATE_LIMIT_SECONDS: int = 60
    EMBEDDING_RETRY_ATTEMPTS: int = 3

    # Rate limiting (with defaults)
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_SECONDS: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create a global settings instance
settings = Settings()