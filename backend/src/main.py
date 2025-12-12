from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from .api.websocket import handle_websocket_connection, get_connection_stats
from .utils.logging import setup_logging

load_dotenv()
logger = setup_logging()

app = FastAPI(
    title="RAG Chatbot Backend",
    description="Live Gemini RAG Tutor for Robotics Book",
    version="1.0.0",
)

# Track startup time for uptime calculation
startup_time = time.time()

# Secure CORS configuration
cors_origins = os.getenv("CORS_ORIGIN", "http://localhost:3000")
if "," in cors_origins:
    cors_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if isinstance(cors_origins, list) else [cors_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Restrict to necessary methods
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-Forwarded-For",
        "X-Real-IP",
        "User-Agent",
    ],  # Restrict to necessary headers
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)


@app.get("/api/health")
async def health_check():
    """Health check endpoint with system status"""
    uptime_seconds = int(time.time() - startup_time)
    connection_stats = get_connection_stats()

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime_seconds": uptime_seconds,
        "active_connections": connection_stats["active_connections"],
    }


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await handle_websocket_connection(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
