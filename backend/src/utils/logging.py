import logging
from src.config import settings

def setup_logging():
    """Configure structured logging for the application."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Set specific log levels for different loggers if needed
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    return logging.getLogger(__name__)

# Create a logger instance
logger = setup_logging()

def get_logger(name: str):
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)