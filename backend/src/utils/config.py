import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    """Application configuration"""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Vector Database
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")

    # AI Service
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv(
        "OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    # Security
    GITHUB_WEBHOOK_SECRET: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    CORS_ORIGIN: str = os.getenv("CORS_ORIGIN", "http://localhost:3000")

    # Performance
    MAX_CONCURRENT_USERS: int = int(os.getenv("MAX_CONCURRENT_USERS", "50"))
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

    # Caching
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

    # Content
    DOCS_ROOT: str = os.getenv("DOCS_ROOT", "../docs")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "content_vectors")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = [
            "DATABASE_URL",
            "QDRANT_URL",
            "QDRANT_API_KEY",
            "GEMINI_API_KEY",
        ]

        missing_vars = [var for var in required_vars if not getattr(cls, var)]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        return True


def get_config() -> Config:
    """Get validated configuration instance"""
    Config.validate()
    return Config()
