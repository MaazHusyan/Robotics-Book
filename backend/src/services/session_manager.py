"""
Session management using SQLiteSession from agents library adapted from rag_agent.py reference file.

This module provides conversation session management with persistent storage.
"""
from agents.memory.sqlite_session import SQLiteSession
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manager for conversation sessions using SQLiteSession from agents library.
    Adapts the SQLiteSession pattern from rag_agent.py reference file.
    """

    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize the session manager.

        Args:
            db_path: Path to SQLite database file. Defaults to in-memory database.
        """
        self.db_path = db_path
        logger.info(f"SessionManager initialized with db_path: {db_path}")

    def get_session(self, session_id: str) -> SQLiteSession:
        """
        Get or create a SQLiteSession for the given session_id.

        Args:
            session_id: Unique identifier for the session

        Returns:
            SQLiteSession instance for the given session_id
        """
        logger.debug(f"Getting SQLiteSession for session_id: {session_id}")
        session = SQLiteSession(session_id=session_id, db_path=self.db_path)
        return session

    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Unique identifier for the session

        Returns:
            List of conversation turns
        """
        session = self.get_session(session_id)
        items = await session.get_items()
        logger.debug(f"Retrieved {len(items)} items from session {session_id}")
        return items

    async def add_conversation_turn(self, session_id: str, turn: Dict[str, Any]) -> None:
        """
        Add a conversation turn to the session.

        Args:
            session_id: Unique identifier for the session
            turn: Conversation turn to add (e.g., {"role": "user", "content": "message"})
        """
        session = self.get_session(session_id)
        await session.add_items([turn])
        logger.debug(f"Added turn to session {session_id}")

    async def clear_session(self, session_id: str) -> None:
        """
        Clear all conversation history for a session.

        Args:
            session_id: Unique identifier for the session
        """
        session = self.get_session(session_id)
        await session.clear_session()
        logger.info(f"Cleared session {session_id}")

    def close_session(self, session_id: str) -> None:
        """
        Close the database connection for a session.

        Args:
            session_id: Unique identifier for the session
        """
        session = self.get_session(session_id)
        session.close()
        logger.debug(f"Closed session {session_id}")


# Global session manager instance
session_manager = SessionManager()