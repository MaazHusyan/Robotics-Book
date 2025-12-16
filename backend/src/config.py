from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    log_level: str = "info"
    allowed_origins: str = "*"  # Comma-separated list of allowed origins
    database_url: Optional[str] = None
    max_request_size: str = "10MB"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"

    class Config:
        env_file = ".env" if os.path.exists(".env") else None
        env_file_encoding = "utf-8"

    @property
    def allowed_origins_list(self) -> list:
        """Convert the allowed_origins string to a list."""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()