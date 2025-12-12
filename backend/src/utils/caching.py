"""
Redis caching utilities for RAG chatbot performance optimization.
Provides connection management, caching strategies, and performance monitoring.
"""

import os
import json
import time
import hashlib
import asyncio
from typing import Any, Optional, Dict, List, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from ..utils.config import get_config
from ..utils.errors import CacheError


logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration for Redis caching."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    max_connections: int = 20
    socket_timeout: int = 5
    socket_connect_timeout: int = 5

    # TTL settings (in seconds)
    embedding_ttl: int = 3600  # 1 hour
    response_ttl: int = 1800  # 30 minutes
    query_ttl: int = 900  # 15 minutes
    session_ttl: int = 86400  # 24 hours

    # Cache sizes
    max_cache_size: int = 10000
    cleanup_interval: int = 300  # 5 minutes


class SimpleCache:
    """Simple in-memory cache fallback when Redis is not available."""

    def __init__(self):
        self._cache = {}
        self._ttl = {}
        self._stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0}

    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired."""
        if key not in self._ttl:
            return True
        return time.time() > self._ttl[key]

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache and not self._is_expired(key):
            self._stats["hits"] += 1
            return self._cache[key]
        else:
            self._stats["misses"] += 1
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        self._cache[key] = value
        if ttl is not None:
            self._ttl[key] = time.time() + ttl
        else:
            self._ttl[key] = time.time() + 3600  # Default 1 hour
        self._stats["sets"] += 1
        return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        deleted = False
        if key in self._cache:
            del self._cache[key]
            deleted = True
        if key in self._ttl:
            del self._ttl[key]
            deleted = True

        if deleted:
            self._stats["deletes"] += 1
        return deleted

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self._cache and not self._is_expired(key)

    async def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        # Simple pattern matching for fallback
        if "*" in pattern:
            prefix = pattern.replace("*", "")
            return [k for k in self._cache.keys() if k.startswith(prefix)]
        return [k for k in self._cache.keys() if k == pattern]

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        keys_to_delete = await self.keys(pattern)
        deleted_count = 0
        for key in keys_to_delete:
            if await self.delete(key):
                deleted_count += 1
        return deleted_count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (
            (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            **self._stats,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests,
            "cache_size": len(self._cache),
        }

    def reset_stats(self):
        """Reset cache statistics."""
        for key in self._stats:
            self._stats[key] = 0


class CacheManager:
    """High-level cache management with multiple cache types."""

    def __init__(self, use_redis: bool = True):
        self.use_redis = use_redis and self._check_redis_available()
        self.cache = SimpleCache() if not self.use_redis else None
        self._connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "last_error": None,
        }

    def _check_redis_available(self) -> bool:
        """Check if Redis is available."""
        try:
            import redis.asyncio as redis

            return True
        except ImportError:
            logger.warning("Redis not available, using in-memory cache")
            return False

    async def initialize(self):
        """Initialize the cache manager."""
        if self.use_redis:
            try:
                import redis.asyncio as redis

                settings = get_config()

                # Create Redis connection pool
                self.redis_pool = redis.ConnectionPool.from_url(
                    f"redis://{getattr(settings, 'REDIS_HOST', 'localhost')}:{getattr(settings, 'REDIS_PORT', 6379)}/{getattr(settings, 'REDIS_DB', 0)}",
                    password=getattr(settings, "REDIS_PASSWORD", None),
                    ssl=getattr(settings, "REDIS_SSL", False),
                    max_connections=getattr(settings, "REDIS_MAX_CONNECTIONS", 20),
                    decode_responses=True,
                )

                # Test connection
                test_client = redis.Redis(connection_pool=self.redis_pool)
                await test_client.ping()

                self._connection_stats["total_connections"] += 1
                logger.info("Redis connection pool initialized")

                # Create Redis cache interface
                self.cache = RedisCache(self)

            except Exception as e:
                self._connection_stats["failed_connections"] += 1
                self._connection_stats["last_error"] = str(e)
                logger.error(f"Failed to initialize Redis: {e}")
                self.use_redis = False
                self.cache = SimpleCache()
        else:
            self.cache = SimpleCache()
            logger.info("Using in-memory cache")

    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate a cache key with prefix."""
        # Use SHA256 for consistent key generation
        hash_input = f"{prefix}:{identifier}"
        return f"ragchat:{hashlib.sha256(hash_input.encode()).hexdigest()[:16]}"

    def _serialize_value(self, value: Any) -> str:
        """Serialize value for storage."""
        if isinstance(value, (dict, list)):
            return json.dumps(value, default=str)
        return str(value)

    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from storage."""
        try:
            # Try JSON first
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # Return as string if not JSON
            return value

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.cache:
            await self.initialize()
        return await self.cache.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        if not self.cache:
            await self.initialize()
        return await self.cache.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.cache:
            await self.initialize()
        return await self.cache.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.cache:
            await self.initialize()
        return await self.cache.exists(key)

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.cache:
            await self.initialize()
        return await self.cache.clear_pattern(pattern)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        if not self.cache:
            return {"error": "Cache not initialized"}

        cache_stats = self.cache.get_stats()
        return {
            **cache_stats,
            "connection_stats": self._connection_stats,
            "cache_type": "redis" if self.use_redis else "memory",
        }

    def reset_stats(self):
        """Reset cache statistics."""
        if self.cache:
            self.cache.reset_stats()


class RedisCache:
    """Redis cache implementation."""

    def __init__(self, manager):
        self.manager = manager
        self.config = self._load_config()

    def _load_config(self) -> CacheConfig:
        """Load Redis configuration from environment."""
        settings = get_config()

        return CacheConfig(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=getattr(settings, "REDIS_PORT", 6379),
            db=getattr(settings, "REDIS_DB", 0),
            password=getattr(settings, "REDIS_PASSWORD", None),
            ssl=getattr(settings, "REDIS_SSL", False),
            embedding_ttl=getattr(settings, "EMBEDDING_CACHE_TTL", 3600),
            response_ttl=getattr(settings, "RESPONSE_CACHE_TTL", 1800),
            query_ttl=getattr(settings, "QUERY_CACHE_TTL", 900),
            session_ttl=getattr(settings, "SESSION_CACHE_TTL", 86400),
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        try:
            import redis.asyncio as redis

            client = redis.Redis(connection_pool=self.manager.redis_pool)
            value = await client.get(key)
            return self._deserialize_value(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis with TTL."""
        try:
            import redis.asyncio as redis

            client = redis.Redis(connection_pool=self.manager.redis_pool)
            serialized_value = self._serialize_value(value)

            if ttl is None:
                return await client.set(key, serialized_value)
            else:
                return await client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from Redis."""
        try:
            import redis.asyncio as redis

            client = redis.Redis(connection_pool=self.manager.redis_pool)
            result = await client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            import redis.asyncio as redis

            client = redis.Redis(connection_pool=self.manager.redis_pool)
            return await client.exists(key)
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False

    async def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        try:
            import redis.asyncio as redis

            client = redis.Redis(connection_pool=self.manager.redis_pool)
            return await client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis keys error for pattern {pattern}: {e}")
            return []

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            import redis.asyncio as redis

            client = redis.Redis(connection_pool=self.manager.redis_pool)
            keys = await client.keys(pattern)

            if keys:
                deleted = await client.delete(*keys)
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Redis clear pattern error for {pattern}: {e}")
            return 0

    def _serialize_value(self, value: Any) -> str:
        """Serialize value for Redis storage."""
        if isinstance(value, (dict, list)):
            return json.dumps(value, default=str)
        return str(value)

    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from Redis storage."""
        try:
            # Try JSON first
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # Return as string if not JSON
            return value


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get or create global cache manager."""
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = CacheManager()
        await _cache_manager.initialize()

    return _cache_manager


class EmbeddingCache:
    """Specialized cache for text embeddings."""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.prefix = "embedding"
        self.ttl = 3600  # 1 hour

    def _get_embedding_key(self, text: str) -> str:
        """Generate cache key for embedding."""
        # Use text hash for consistent keys
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        return self.cache._generate_key(self.prefix, text_hash)

    async def get(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text."""
        key = self._get_embedding_key(text)
        result = await self.cache.get(key)

        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "embedding" in result:
            return result["embedding"]

        return None

    async def set(self, text: str, embedding: List[float]) -> bool:
        """Cache embedding for text."""
        key = self._get_embedding_key(text)
        value = {
            "embedding": embedding,
            "text_length": len(text),
            "cached_at": datetime.now().isoformat(),
        }
        return await self.cache.set(key, value, self.ttl)

    async def clear(self):
        """Clear all embedding cache."""
        pattern = self.cache._generate_key(self.prefix, "*")
        return await self.cache.clear_pattern(pattern)


class ResponseCache:
    """Specialized cache for query responses."""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.prefix = "response"
        self.ttl = 1800  # 30 minutes

    def _get_response_key(self, query: str, context: Optional[List[str]] = None) -> str:
        """Generate cache key for response."""
        # Include context in key for accurate caching
        context_str = "|".join(sorted(context)) if context else ""
        key_data = f"{query}:{context_str}"
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        return self.cache._generate_key(self.prefix, key_hash)

    async def get(
        self, query: str, context: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached response for query."""
        key = self._get_response_key(query, context)
        return await self.cache.get(key)

    async def set(
        self,
        query: str,
        response: str,
        context: Optional[List[str]] = None,
        sources: Optional[List[Dict]] = None,
    ) -> bool:
        """Cache response for query."""
        key = self._get_response_key(query, context)
        value = {
            "response": response,
            "query": query,
            "context": context,
            "sources": sources,
            "cached_at": datetime.now().isoformat(),
        }
        return await self.cache.set(key, value, self.ttl)

    async def clear(self):
        """Clear all response cache."""
        pattern = self.cache._generate_key(self.prefix, "*")
        return await self.cache.clear_pattern(pattern)


# Health check function
async def cache_health_check() -> Dict[str, Any]:
    """Perform health check on caching system."""
    try:
        cache_mgr = await get_cache_manager()

        # Test basic operations
        test_key = "health_check_test"
        test_value = {"test": True, "timestamp": time.time()}

        # Test set
        set_success = await cache_mgr.set(test_key, test_value, 10)

        # Test get
        retrieved_value = await cache_mgr.get(test_key)

        # Test delete
        delete_success = await cache_mgr.delete(test_key)

        # Get stats
        stats = cache_mgr.get_stats()

        health_status = {
            "status": "healthy"
            if all([set_success, retrieved_value == test_value, delete_success])
            else "unhealthy",
            "operations_test": {
                "set": set_success,
                "get": retrieved_value == test_value,
                "delete": delete_success,
            },
            "cache_stats": stats,
            "timestamp": datetime.now().isoformat(),
        }

        return health_status

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
