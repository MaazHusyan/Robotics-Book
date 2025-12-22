"""
Main FastAPI application for the RAG Chatbot
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from contextlib import asynccontextmanager

from src.retrieval.api.retrieval_endpoint import router as retrieval_router
from src.api.agent_endpoint import router as agent_router
# Remove the settings import as it's not needed for this implementation


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for application startup and shutdown
    """
    logger.info("Starting RAG Chatbot application...")
    # Startup logic here
    yield
    # Shutdown logic here
    logger.info("Shutting down RAG Chatbot application...")


# Create FastAPI app instance
app = FastAPI(
    title="RAG Chatbot API",
    description="API for Retrieval-Augmented Generation chatbot that answers questions from robotics book content",
    version="1.0.0",
    lifespan=lifespan
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include retrieval API routes
app.include_router(retrieval_router)
# Include agent API routes
app.include_router(agent_router)


@app.get("/")
async def root():
    """
    Root endpoint for health check
    """
    return {"message": "RAG Chatbot API is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "RAG Chatbot API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Set to False in production
    )