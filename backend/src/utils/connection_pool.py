"""
Connection pooling utilities for database and external service connections.
Provides efficient connection management and monitoring.
"""

import asyncio
import time
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from ..utils.config import get_config
from ..utils.errors import DatabaseError, CacheError


logger = logging.getLogger(__name__)


@dataclass
class PoolConfig:
    """Configuration for connection pools."""

    min_connections: int = 2
    max_connections: int = 20
    connection_timeout: float = 30.0
    idle_timeout: float = 300.0  # 5 minutes
    max_lifetime: float = 3600.0  # 1 hour
    retry_attempts: int = 3
    retry_delay: float = 1.0
    health_check_interval: float = 60.0  # 1 minute

    # Database specific
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str = "postgres"
    db_password: Optional[str] = None

    # Redis specific
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None


class ConnectionWrapper:
    """Wrapper for connections with metadata."""

    def __init__(self, connection: Any, pool: "BasePool"):
        self.connection = connection
        self.pool = pool
        self.created_at = time.time()
        self.last_used = time.time()
        self.in_use = False
        self.is_healthy = True
        self.use_count = 0

    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with connection."""
        self.last_used = time.time()
        self.use_count += 1
        self.in_use = True

        try:
            return await func(self.connection, *args, **kwargs)
        finally:
            self.in_use = False

    def is_expired(self, max_lifetime: float) -> bool:
        """Check if connection is expired."""
        return (time.time() - self.created_at) > max_lifetime

    def is_idle(self, idle_timeout: float) -> bool:
        """Check if connection is idle."""
        return not self.in_use and (time.time() - self.last_used) > idle_timeout

    async def health_check(self) -> bool:
        """Perform health check on connection."""
        try:
            # Default health check - can be overridden
            if hasattr(self.connection, "ping"):
                await self.connection.ping()
            elif hasattr(self.connection, "execute"):
                await self.connection.execute("SELECT 1")
            else:
                # Connection doesn't support health checks
                return True

            self.is_healthy = True
            return True
        except Exception as e:
            self.is_healthy = False
            logger.warning(f"Connection health check failed: {e}")
            return False


class BasePool:
    """Base class for connection pools."""

    def __init__(self, config: PoolConfig):
        self.config = config
        self.connections: List[ConnectionWrapper] = []
        self.semaphore = None
        self.stats = {
            "total_created": 0,
            "total_destroyed": 0,
            "active_connections": 0,
            "idle_connections": 0,
            "health_checks": 0,
            "failed_health_checks": 0,
            "last_cleanup": time.time(),
        }
        self._cleanup_task = None
        self._running = False

    async def initialize(self):
        """Initialize connection pool."""
        if self._running:
            return

        self._running = True

        # Create initial connections
        for _ in range(self.config.min_connections):
            await self._create_connection()

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info(
            f"Connection pool initialized with {self.config.min_connections} connections"
        )

    async def _create_connection(self) -> Optional[ConnectionWrapper]:
        """Create a new connection."""
        try:
            raw_connection = await self._create_raw_connection()
            if raw_connection is None:
                return None

            wrapper = ConnectionWrapper(raw_connection, self)
            self.connections.append(wrapper)
            self.stats["total_created"] += 1
            self.stats["active_connections"] += 1

            return wrapper

        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
            return None

    async def _create_raw_connection(self) -> Any:
        """Create raw connection - to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _create_raw_connection")

    async def get_connection(
        self, timeout: Optional[float] = None
    ) -> Optional[ConnectionWrapper]:
        """Get a connection from the pool."""
        timeout = timeout or self.config.connection_timeout

        async with self.semaphore:
            # Try to find an existing idle connection
            for wrapper in self.connections:
                if not wrapper.in_use and wrapper.is_healthy:
                    if wrapper.is_idle(self.config.idle_timeout):
                        # Connection is idle, perform health check
                        if await wrapper.health_check():
                            return wrapper
                        else:
                            # Remove unhealthy connection
                            await self._destroy_connection(wrapper)
                    else:
                        # Connection is fresh and healthy
                        return wrapper

            # No available connection, create new one if under max
            if len(self.connections) < self.config.max_connections:
                wrapper = await self._create_connection()
                if wrapper:
                    return wrapper

            # Pool is full and no available connections
            logger.warning("Connection pool exhausted")
            return None

    @asynccontextmanager
    async def connection(self, timeout: Optional[float] = None):
        """Context manager for getting and returning connections."""
        wrapper = await self.get_connection(timeout)
        if wrapper is None:
            raise DatabaseError("No available connections in pool")

        try:
            yield wrapper
        finally:
            # Connection is automatically returned to pool
            pass

    async def return_connection(self, wrapper: ConnectionWrapper):
        """Return a connection to the pool (implicitly handled by wrapper)."""
        # Connection wrapper handles state automatically
        pass

    async def _destroy_connection(self, wrapper: ConnectionWrapper):
        """Destroy a connection."""
        try:
            if hasattr(wrapper.connection, "close"):
                await wrapper.connection.close()
            elif hasattr(wrapper.connection, "disconnect"):
                await wrapper.connection.disconnect()

            if wrapper in self.connections:
                self.connections.remove(wrapper)
                self.stats["total_destroyed"] += 1
                self.stats["active_connections"] -= 1

        except Exception as e:
            logger.error(f"Error destroying connection: {e}")

    async def _cleanup_loop(self):
        """Periodic cleanup of expired and idle connections."""
        while self._running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._cleanup_connections()
                self.stats["last_cleanup"] = time.time()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

    async def _cleanup_connections(self):
        """Clean up expired and unhealthy connections."""
        connections_to_remove = []

        for wrapper in self.connections:
            should_remove = False

            # Check if connection is expired
            if wrapper.is_expired(self.config.max_lifetime):
                should_remove = True
                logger.debug("Removing expired connection")

            # Check if connection is idle and unhealthy
            elif wrapper.is_idle(self.config.idle_timeout) and not wrapper.is_healthy:
                should_remove = True
                logger.debug("Removing idle unhealthy connection")

            # Perform health check on idle connections
            elif wrapper.is_idle(self.config.idle_timeout):
                self.stats["health_checks"] += 1
                if not await wrapper.health_check():
                    should_remove = True
                    self.stats["failed_health_checks"] += 1
                    logger.debug("Removing connection that failed health check")

            if should_remove:
                connections_to_remove.append(wrapper)

        # Remove marked connections
        for wrapper in connections_to_remove:
            await self._destroy_connection(wrapper)

        if connections_to_remove:
            logger.debug(f"Cleaned up {len(connections_to_remove)} connections")

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        active_count = sum(1 for w in self.connections if w.in_use)
        idle_count = len(self.connections) - active_count

        return {
            **self.stats,
            "total_connections": len(self.connections),
            "active_connections": active_count,
            "idle_connections": idle_count,
            "pool_utilization": round(
                active_count / self.config.max_connections * 100, 1
            ),
            "config": {
                "min_connections": self.config.min_connections,
                "max_connections": self.config.max_connections,
                "connection_timeout": self.config.connection_timeout,
                "idle_timeout": self.config.idle_timeout,
            },
        }

    async def close(self):
        """Close all connections and shutdown pool."""
        self._running = False

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Close all connections
        for wrapper in self.connections.copy():
            await self._destroy_connection(wrapper)

        logger.info("Connection pool closed")


class DatabasePool(BasePool):
    """Connection pool for PostgreSQL database."""

    def __init__(self, config: Optional[PoolConfig] = None):
        if config is None:
            settings = get_config()
            config = PoolConfig(
                db_host=getattr(settings, "DB_HOST", "localhost"),
                db_port=getattr(settings, "DB_PORT", 5432),
                db_name=getattr(settings, "DB_NAME", "postgres"),
                db_user=getattr(settings, "DB_USER", "postgres"),
                db_password=getattr(settings, "DB_PASSWORD", None),
            )

        super().__init__(config)

    async def _create_raw_connection(self) -> Any:
        """Create a new database connection."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            connection = psycopg2.connect(
                host=self.config.db_host,
                port=self.config.db_port,
                database=self.config.db_name,
                user=self.config.db_user,
                password=self.config.db_password,
                cursor_factory=RealDictCursor,
            )

            # Test connection
            with connection.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()

            return connection

        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            return None


class RedisPool(BasePool):
    """Connection pool for Redis."""

    def __init__(self, config: Optional[PoolConfig] = None):
        if config is None:
            settings = get_config()
            config = PoolConfig(
                redis_host=getattr(settings, "REDIS_HOST", "localhost"),
                redis_port=getattr(settings, "REDIS_PORT", 6379),
                redis_db=getattr(settings, "REDIS_DB", 0),
                redis_password=getattr(settings, "REDIS_PASSWORD", None),
            )

        super().__init__(config)

    async def _create_raw_connection(self) -> Any:
        """Create a new Redis connection."""
        try:
            import redis.asyncio as redis

            connection = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                decode_responses=True,
                socket_connect_timeout=self.config.connection_timeout,
                socket_timeout=self.config.connection_timeout,
            )

            # Test connection
            await connection.ping()

            return connection

        except Exception as e:
            logger.error(f"Failed to create Redis connection: {e}")
            return None


# Global pool instances
_db_pool: Optional[DatabasePool] = None
_redis_pool: Optional[RedisPool] = None


async def get_database_pool(config: Optional[PoolConfig] = None) -> DatabasePool:
    """Get or create database connection pool."""
    global _db_pool

    if _db_pool is None:
        _db_pool = DatabasePool(config)
        await _db_pool.initialize()

    return _db_pool


async def get_redis_pool(config: Optional[PoolConfig] = None) -> RedisPool:
    """Get or create Redis connection pool."""
    global _redis_pool

    if _redis_pool is None:
        _redis_pool = RedisPool(config)
        await _redis_pool.initialize()

    return _redis_pool


async def close_all_pools():
    """Close all connection pools."""
    global _db_pool, _redis_pool

    if _db_pool:
        await _db_pool.close()
        _db_pool = None

    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None


# Health check for all pools
async def pool_health_check() -> Dict[str, Any]:
    """Perform health check on all connection pools."""
    health_status = {"timestamp": datetime.now().isoformat(), "pools": {}}

    if _db_pool:
        db_stats = _db_pool.get_stats()
        health_status["pools"]["database"] = {
            "status": "healthy" if db_stats["active_connections"] >= 0 else "unhealthy",
            "stats": db_stats,
        }

    if _redis_pool:
        redis_stats = _redis_pool.get_stats()
        health_status["pools"]["redis"] = {
            "status": "healthy"
            if redis_stats["active_connections"] >= 0
            else "unhealthy",
            "stats": redis_stats,
        }

    return health_status


# Decorator for using database connections
def with_db_connection(func):
    """Decorator to provide database connection from pool."""

    async def wrapper(*args, **kwargs):
        pool = await get_database_pool()
        async with pool.connection() as wrapper:
            return await wrapper.execute(func, *args, **kwargs)

    return wrapper


# Decorator for using Redis connections
def with_redis_connection(func):
    """Decorator to provide Redis connection from pool."""

    async def wrapper(*args, **kwargs):
        pool = await get_redis_pool()
        async with pool.connection() as wrapper:
            return await wrapper.execute(func, *args, **kwargs)

    return wrapper
