import json
import asyncio
import uuid
import hashlib
import time
import html
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from ..utils.logging import get_logger
from ..utils.errors import RAGError
from ..services.rag_agent import RAGAgentService

logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and sessions with security features"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_data: Dict[str, dict] = {}
        self.connection_attempts: Dict[str, List[datetime]] = {}  # Rate limiting
        self.banned_ips: Dict[str, datetime] = {}  # IP bans

    async def connect(
        self, websocket: WebSocket, session_id: Optional[str] = None
    ) -> str:
        """Accept and register a new WebSocket connection with security checks"""
        # Get client IP for security
        client_ip = websocket.client.host if websocket.client else "unknown"

        # Check if IP is banned
        if client_ip in self.banned_ips:
            if self.banned_ips[client_ip] > datetime.utcnow():
                logger.warning(f"Rejected connection from banned IP: {client_ip}")
                raise HTTPException(status_code=403, detail="IP banned")
            else:
                # Ban expired, remove it
                del self.banned_ips[client_ip]

        # Check connection rate limiting
        now = datetime.utcnow()
        if client_ip not in self.connection_attempts:
            self.connection_attempts[client_ip] = []

        # Remove old attempts (older than 1 minute)
        self.connection_attempts[client_ip] = [
            attempt
            for attempt in self.connection_attempts[client_ip]
            if now - attempt < timedelta(minutes=1)
        ]

        # Check if too many connections
        if len(self.connection_attempts[client_ip]) > 10:  # 10 connections per minute
            logger.warning(f"Rate limiting connection from IP: {client_ip}")
            # Ban for 5 minutes
            self.banned_ips[client_ip] = now + timedelta(minutes=5)
            raise HTTPException(status_code=429, detail="Too many connection attempts")

        # Record this attempt
        self.connection_attempts[client_ip].append(now)

        await websocket.accept()

        if not session_id:
            session_id = str(uuid.uuid4())

        self.active_connections[session_id] = websocket
        self.session_data[session_id] = {
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "message_count": 0,
            "ip_address": client_ip,
            "user_agent": websocket.headers.get("user-agent", "unknown"),
            "authenticated": False,  # Always false for anonymous system
        }

        logger.info(f"WebSocket connection established: {session_id} from {client_ip}")
        return session_id

    def disconnect(self, session_id: str):
        """Remove a WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.session_data:
            del self.session_data[session_id]
        logger.info(f"WebSocket connection closed: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        """Send a message to a specific session"""
        if session_id and session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_text(json.dumps(message))
                if session_id in self.session_data:
                    self.session_data[session_id]["last_activity"] = datetime.utcnow()
                    self.session_data[session_id]["message_count"] += 1
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                self.disconnect(session_id)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        for session_id in list(self.active_connections.keys()):
            await self.send_message(session_id, message)


# Global connection manager
manager = ConnectionManager()


async def handle_websocket_connection(websocket: WebSocket):
    """Main WebSocket connection handler"""
    session_id = None
    agent = None

    try:
        # Establish connection
        session_id = await manager.connect(websocket)

        # Initialize RAG agent
        agent = create_robotics_tutor_agent()

        # Send welcome message
        await manager.send_message(
            session_id,
            {
                "type": "welcome",
                "data": {
                    "session_id": session_id,
                    "server_version": "1.0.0",
                    "features": ["text_selection", "streaming", "source_citation"],
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        # Main message loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

        # Update session activity and check rate limiting
        if session_id in manager.session_data:
            session_data = manager.session_data[session_id]
            session_data["last_activity"] = datetime.utcnow()

            # Simple rate limiting: max 30 messages per minute per session
            now = datetime.utcnow()
            if "message_timestamps" not in session_data:
                session_data["message_timestamps"] = []

            # Remove old timestamps (older than 1 minute)
            session_data["message_timestamps"] = [
                ts
                for ts in session_data["message_timestamps"]
                if now - ts < timedelta(minutes=1)
            ]

            # Check rate limit
            if len(session_data["message_timestamps"]) >= 30:
                await manager.send_message(
                    session_id,
                    {
                        "type": "error",
                        "data": {
                            "code": "RATE_LIMITED",
                            "message": "Too many messages. Please wait a moment.",
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                return

            # Record this message timestamp
            session_data["message_timestamps"].append(now)

        # Handle different message types
        await handle_message(session_id, message, agent)

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON received from {session_id}: {e}")
        if session_id:
            await manager.send_message(
                session_id,
                {
                    "type": "error",
                    "data": {
                        "code": "INVALID_MESSAGE",
                        "message": "Invalid JSON format",
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        if session_id:
            await manager.send_message(
                session_id,
                {
                    "type": "error",
                    "data": {
                        "code": "SERVICE_UNAVAILABLE",
                        "message": "Internal server error",
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
    finally:
        if session_id:
            manager.disconnect(session_id)


async def handle_message(session_id: str, message: dict, agent):
    """Handle incoming WebSocket messages with security validation"""
    # Basic message structure validation
    if not isinstance(message, dict):
        await manager.send_message(
            session_id,
            {
                "type": "error",
                "data": {
                    "code": "INVALID_MESSAGE",
                    "message": "Message must be a JSON object",
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        return

    message_type = message.get("type")
    if not message_type or not isinstance(message_type, str):
        await manager.send_message(
            session_id,
            {
                "type": "error",
                "data": {
                    "code": "INVALID_MESSAGE",
                    "message": "Message must include a valid 'type' field",
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        return

    # Message size validation
    message_str = json.dumps(message)
    if len(message_str) > 10000:  # 10KB limit
        await manager.send_message(
            session_id,
            {
                "type": "error",
                "data": {
                    "code": "MESSAGE_TOO_LARGE",
                    "message": "Message exceeds maximum size limit",
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        return

    if message_type == "question":
        await handle_question(session_id, message, agent)
    elif message_type == "ping":
        await handle_ping(session_id)
    else:
        await manager.send_message(
            session_id,
            {
                "type": "error",
                "data": {
                    "code": "INVALID_MESSAGE",
                    "message": f"Unknown message type: {message_type}",
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


async def handle_question(session_id: str, message: dict, agent):
    """Handle question messages and stream responses with security validation"""
    try:
        question_data = message.get("data", {})
        question = question_data.get("question", "")
        context_chunks = question_data.get("context_chunks", [])

        # Basic input sanitization
        if question:
            # Remove potential HTML/JS
            import html

            question = html.unescape(question)
            # Remove control characters
            import re

            question = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", question)
            question = question.strip()

        # Validate question
        if not question or len(question.strip()) == 0:
            await manager.send_message(
                session_id,
                {
                    "type": "error",
                    "data": {
                        "code": "INVALID_MESSAGE",
                        "message": "Question cannot be empty",
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            return

        if len(question) > 1000:
            await manager.send_message(
                session_id,
                {
                    "type": "error",
                    "data": {
                        "code": "QUESTION_TOO_LONG",
                        "message": "Question exceeds 1000 characters",
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            return

        # Validate context chunks
        if context_chunks:
            if not isinstance(context_chunks, list):
                await manager.send_message(
                    session_id,
                    {
                        "type": "error",
                        "data": {
                            "code": "INVALID_MESSAGE",
                            "message": "Context chunks must be an array",
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                return

            if len(context_chunks) > 5:
                await manager.send_message(
                    session_id,
                    {
                        "type": "error",
                        "data": {
                            "code": "INVALID_MESSAGE",
                            "message": "Maximum 5 context chunks allowed",
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                return

            # Sanitize context chunks
            sanitized_chunks = []
            for chunk in context_chunks:
                if isinstance(chunk, str) and len(chunk.strip()) > 0:
                    sanitized_chunk = html.unescape(chunk)
                    sanitized_chunk = re.sub(
                        r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized_chunk
                    )
                    sanitized_chunks.append(sanitized_chunk.strip())

            context_chunks = sanitized_chunks

        # Generate query ID
        query_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        # Send response start message
        await manager.send_message(
            session_id,
            {
                "type": "response_start",
                "data": {"query_id": query_id, "estimated_duration": 1500},
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        # Process question with agent (placeholder for now)
        # This will be implemented in Phase 3 with actual RAG functionality
        response_content = f"This is a placeholder response to: {question}"

        # Stream response chunks
        words = response_content.split()
        current_chunk = ""

        for i, word in enumerate(words):
            current_chunk += word + " "

            # Send chunk every 5 words or at the end
            if (i + 1) % 5 == 0 or i == len(words) - 1:
                await manager.send_message(
                    session_id,
                    {
                        "type": "response_chunk",
                        "data": {
                            "content": current_chunk.strip(),
                            "is_complete": i == len(words) - 1,
                            "sources": [],  # Will be populated with actual sources in Phase 3
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                current_chunk = ""
                await asyncio.sleep(0.1)  # Simulate streaming delay

        # Calculate response time
        end_time = datetime.utcnow()
        response_time_ms = int((end_time - start_time).total_seconds() * 1000)

        # Send response end message
        await manager.send_message(
            session_id,
            {
                "type": "response_end",
                "data": {
                    "query_id": query_id,
                    "response_time_ms": response_time_ms,
                    "total_tokens": len(response_content.split()),
                    "sources_used": 0,
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"Error handling question for {session_id}: {e}")
        await manager.send_message(
            session_id,
            {
                "type": "error",
                "data": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "Failed to process question",
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


async def handle_ping(session_id: str):
    """Handle ping messages"""
    await manager.send_message(
        session_id,
        {"type": "pong", "data": {}, "timestamp": datetime.utcnow().isoformat()},
    )


def cleanup_expired_sessions():
    """Clean up expired sessions and banned IPs"""
    now = datetime.utcnow()
    cutoff_time = now - timedelta(hours=24)  # 24 hour retention

    # Clean up expired sessions
    expired_sessions = []
    for session_id, session_data in manager.session_data.items():
        if session_data["last_activity"] < cutoff_time:
            expired_sessions.append(session_id)

    for session_id in expired_sessions:
        manager.disconnect(session_id)

    # Clean up expired IP bans
    expired_bans = []
    for ip, ban_time in manager.banned_ips.items():
        if ban_time <= now:
            expired_bans.append(ip)

    for ip in expired_bans:
        del manager.banned_ips[ip]

    if expired_sessions:
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    if expired_bans:
        logger.info(f"Cleaned up {len(expired_bans)} expired IP bans")


def get_connection_stats() -> dict:
    """Get current connection statistics"""
    return {
        "active_connections": len(manager.active_connections),
        "total_sessions": len(manager.session_data),
        "banned_ips": len(manager.banned_ips),
        "connections": list(manager.active_connections.keys()),
    }
