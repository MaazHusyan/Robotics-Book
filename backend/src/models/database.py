import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import logging

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Connection pool for better performance
db_pool = SimpleConnectionPool(minconn=1, maxconn=20, dsn=DATABASE_URL)

logger = logging.getLogger(__name__)


def get_db_connection():
    """Get a database connection from the pool"""
    try:
        return db_pool.getconn()
    except Exception as e:
        logger.error(f"Failed to get database connection: {e}")
        raise


def execute_query(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """Execute a query and return results as list of dictionaries"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise
    finally:
        if conn:
            db_pool.putconn(conn)


def execute_query_single(
    query: str, params: Optional[tuple] = None
) -> Optional[Dict[str, Any]]:
    """Execute a query and return a single result or None"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            return cur.fetchone()
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise
    finally:
        if conn:
            db_pool.putconn(conn)


def create_tables():
    """Create all required database tables"""
    tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS content_chunks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            content TEXT NOT NULL CHECK (length(content) BETWEEN 500 AND 1000),
            source_file VARCHAR(255) NOT NULL,
            chapter VARCHAR(50) NOT NULL,
            section VARCHAR(100),
            chunk_index INTEGER NOT NULL,
            chunk_type VARCHAR(20) NOT NULL DEFAULT 'paragraph',
            token_count INTEGER NOT NULL CHECK (token_count > 0),
            embedding_id VARCHAR(64),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            CONSTRAINT valid_chunk_type CHECK (chunk_type IN ('paragraph', 'section', 'code', 'list'))
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id VARCHAR(64) PRIMARY KEY,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            message_count INTEGER DEFAULT 0 CHECK (message_count >= 0),
            ip_address INET NOT NULL,
            user_agent_hash VARCHAR(64) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS query_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            query_hash VARCHAR(64) NOT NULL,
            question_length INTEGER NOT NULL CHECK (question_length > 0),
            context_provided BOOLEAN DEFAULT FALSE,
            response_length INTEGER NOT NULL CHECK (response_length >= 0),
            sources_count INTEGER DEFAULT 0 CHECK (sources_count >= 0),
            response_time_ms INTEGER NOT NULL CHECK (response_time_ms >= 0),
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            date_bucket VARCHAR(10) NOT NULL
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_content_chunks_source_file ON content_chunks(source_file);
        CREATE INDEX IF NOT EXISTS idx_content_chunks_chapter ON content_chunks(chapter);
        CREATE INDEX IF NOT EXISTS idx_content_chunks_embedding_id ON content_chunks(embedding_id);
        CREATE INDEX IF NOT EXISTS idx_content_chunks_content_hash ON content_chunks(content_hash);
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at);
        CREATE INDEX IF NOT EXISTS idx_query_logs_timestamp ON query_logs(timestamp);
        CREATE INDEX IF NOT EXISTS idx_query_logs_date_bucket ON query_logs(date_bucket);
        """,
        """
        CREATE TABLE IF NOT EXISTS chapter_stats (
            chapter VARCHAR(50) PRIMARY KEY,
            chunk_count INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            avg_tokens_per_chunk DECIMAL(10,2),
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS file_stats (
            source_file VARCHAR(255) PRIMARY KEY,
            chunk_count INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            avg_tokens_per_chunk DECIMAL(10,2),
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
    ]

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            for table_sql in tables_sql:
                cur.execute(table_sql)
            conn.commit()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            db_pool.putconn(conn)
