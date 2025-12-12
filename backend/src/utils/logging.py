import logging
import os
from .config import get_config

def setup_logging():
    """Setup logging configuration"""
    config = get_config()
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('rag_chatbot.log')
        ]
    )
    
    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    
    return logger

def get_logger(name: str):
    """Get a logger instance"""
    return logging.getLogger(name)

if __name__ == "__main__":
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Logging test successful")
