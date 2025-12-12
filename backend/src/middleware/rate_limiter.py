"""
Rate limiting middleware for RAG chatbot API protection.
Provides IP-based and token-based rate limiting with configurable policies.
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import hashlib
import ipaddress
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from ..utils.config import get_config
from ..utils.errors import RateLimitError
from ..utils.caching import get_cache_manager


logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    # General settings
    enabled: bool = True
    default_limit: int = 100  # requests per window
    window_seconds: int = 60  # time window
    burst_limit: int = 200  # allow burst above normal limit

    # IP-based settings
    ip_enabled: bool = True
    ip_limit: int = 50  # requests per window per IP
    ip_window_seconds: int = 300  # 5 minutes
    ip_block_duration: int = 3600  # 1 hour block

    # Token-based settings (for authenticated users)
    token_enabled: bool = False  # Not used for anonymous access
    token_limit: int = 1000  # requests per window per token
    token_window_seconds: int = 3600  # 1 hour

    # Whitelist settings
    whitelist_enabled: bool = True
    whitelist_ips: List[str] = field(default_factory=list)
    whitelist_paths: List[str] = field(
        default_factory=lambda: ["/health", "/metrics", "/api/health"]
    )

    # Response settings
    response_headers: Dict[str, str] = field(
        default_factory=lambda: {
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "60",
            "X-RateLimit-Retry-After": "60",
        }
    )


@dataclass
class ClientInfo:
    """Information about a client for rate limiting."""

    ip_address: str
    user_agent: str
    request_count: int = 0
    first_request: datetime = field(default_factory=datetime.now)
    last_request: datetime = field(default_factory=datetime.now)
    blocked_until: Optional[datetime] = None
    violations: int = 0

    def is_blocked(self) -> bool:
        """Check if client is currently blocked."""
        return self.blocked_until is not None and self.blocked_until > datetime.now()

    def block(self, duration_seconds: int):
        """Block client for specified duration."""
        self.blocked_until = datetime.now() + timedelta(seconds=duration_seconds)
        self.violations += 1
        logger.warning(
            f"Blocked client {self.ip_address} for {duration_seconds} seconds"
        )

    def unblock(self):
        """Unblock client."""
        self.blocked_until = None
        logger.info(f"Unblocked client {self.ip_address}")

    def update_request(self):
        """Update request tracking."""
        now = datetime.now()
        self.last_request = now
        self.request_count += 1


class RateLimiter:
    """Main rate limiting implementation."""

    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.clients: Dict[str, ClientInfo] = {}
        self.global_stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "violations": 0,
            "active_clients": 0,
            "start_time": datetime.now(),
        }
        self.cache_manager = None
        self._cleanup_task = None
        self._running = False

    async def initialize(self):
        """Initialize rate limiter."""
        if not self.config.enabled:
            logger.info("Rate limiting disabled")
            return

        self.cache_manager = await get_cache_manager()
        self._running = True

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("Rate limiter initialized")

    def _get_client_key(self, request: Request) -> str:
        """Generate client identifier for rate limiting."""
        # Use IP address as primary key
        client_ip = self._get_client_ip(request)
        return client_ip

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        # Check for forwarded headers (common in load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the list
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to client IP
        return request.client.host if request.client else "unknown"

    def _get_user_agent(self, request: Request) -> str:
        """Extract and hash user agent for client identification."""
        user_agent = request.headers.get("User-Agent", "")
        if user_agent:
            # Hash user agent for privacy but maintain consistency
            return hashlib.md5(user_agent.encode()).hexdigest()[:16]
        return "unknown"

    def _is_whitelisted(self, request: Request) -> bool:
        """Check if request should bypass rate limiting."""
        # Check IP whitelist
        client_ip = self._get_client_ip(request)
        if client_ip in self.config.whitelist_ips:
            return True

        # Check path whitelist
        path = request.url.path
        if any(
            path.startswith(whitelist_path)
            for whitelist_path in self.config.whitelist_paths
        ):
            return True

        return False

    def _is_violation(self, client_info: ClientInfo) -> bool:
        """Check if client has exceeded rate limits."""
        if client_info.is_blocked():
            return True

        # Check time window
        now = datetime.now()
        window_start = now - timedelta(seconds=self.config.window_seconds)

        # Count requests in window
        requests_in_window = 1  # Current request

        # If this is the first request in window, no violation
        if client_info.first_request < window_start:
            return False

        # For simplicity, use request count as approximation
        # In production, you'd want to store actual request timestamps
        return client_info.request_count > self.config.default_limit

    def _is_ip_violation(self, client_info: ClientInfo) -> bool:
        """Check if IP has exceeded rate limits."""
        if client_info.is_blocked():
            return True

        # Check IP-specific time window
        now = datetime.now()
        ip_window_start = now - timedelta(seconds=self.config.ip_window_seconds)

        # Count requests in IP window (simplified)
        # In production, track actual request timestamps per IP
        return client_info.request_count > self.config.ip_limit

    async def check_rate_limit(self, request: Request) -> Optional[Dict[str, Any]]:
        """Check if request exceeds rate limits."""
        if not self.config.enabled or self._is_whitelisted(request):
            return None

        client_key = self._get_client_key(request)
        client_info = self.clients.get(client_key)

        if client_info is None:
            # New client
            client_info = ClientInfo(
                ip_address=self._get_client_ip(request),
                user_agent=self._get_user_agent(request),
            )
            self.clients[client_key] = client_info
            self.global_stats["active_clients"] += 1

        # Update request info
        client_info.update_request()

        # Check for violations
        is_violation = self._is_violation(client_info)
        is_ip_violation = self.config.ip_enabled and self._is_ip_violation(client_info)

        if is_violation or is_ip_violation:
            # Handle violation
            if is_ip_violation:
                client_info.block(self.config.ip_block_duration)
                self.global_stats["blocked_requests"] += 1
            else:
                self.global_stats["violations"] += 1

            return {
                "error": "rate_limit_exceeded",
                "message": "Rate limit exceeded",
                "retry_after": self.config.window_seconds,
                "limit": self.config.default_limit,
                "remaining": 0,
                "reset_time": (
                    datetime.now() + timedelta(seconds=self.config.window_seconds)
                ).isoformat(),
                "client_id": client_key,
                "violation_type": "global" if is_violation else "ip",
            }

        # Update remaining requests
        remaining = max(0, self.config.default_limit - client_info.request_count)

        return {
            "remaining": remaining,
            "limit": self.config.default_limit,
            "reset_time": (
                client_info.first_request
                + timedelta(seconds=self.config.window_seconds)
            ).isoformat(),
            "client_id": client_key,
        }

    def _get_rate_limit_headers(self, limit_info: Dict[str, Any]) -> Dict[str, str]:
        """Get rate limit response headers."""
        headers = self.config.response_headers.copy()

        if "retry_after" in limit_info:
            headers["X-RateLimit-Reset"] = limit_info["retry_after"]

        if "remaining" in limit_info:
            headers["X-RateLimit-Remaining"] = str(limit_info["remaining"])

        if "limit" in limit_info:
            headers["X-RateLimit-Limit"] = str(limit_info["limit"])

        return headers

    async def _cleanup_loop(self):
        """Periodic cleanup of old client data."""
        while self._running:
            try:
                await asyncio.sleep(300)  # Clean every 5 minutes
                self._cleanup_old_clients()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    def _cleanup_old_clients(self):
        """Remove old client data to prevent memory leaks."""
        cutoff_time = datetime.now() - timedelta(hours=1)  # Keep 1 hour of data

        clients_to_remove = []
        for client_key, client_info in self.clients.items():
            if client_info.last_request < cutoff_time and not client_info.is_blocked():
                clients_to_remove.append(client_key)

        for client_key in clients_to_remove:
            del self.clients[client_key]

        if clients_to_remove:
            logger.debug(f"Cleaned up {len(clients_to_remove)} old client records")

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        uptime = datetime.now() - self.global_stats["start_time"]

        return {
            **self.global_stats,
            "uptime_seconds": uptime.total_seconds(),
            "active_clients": len(self.clients),
            "blocked_clients": len(
                [c for c in self.clients.values() if c.is_blocked()]
            ),
            "config": {
                "enabled": self.config.enabled,
                "default_limit": self.config.default_limit,
                "window_seconds": self.config.window_seconds,
                "ip_enabled": self.config.ip_enabled,
                "ip_limit": self.config.ip_limit,
                "whitelisted_ips": len(self.config.whitelist_ips),
                "whitelisted_paths": len(self.config.whitelist_paths),
            },
        }

    async def close(self):
        """Close rate limiter."""
        self._running = False

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("Rate limiter closed")


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting."""

    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.limiter = RateLimiter(config)

    async def __call__(self, request: Request, call_next: Callable):
        """Middleware call handler."""
        await self.limiter.initialize()

        # Check rate limit
        limit_result = await self.limiter.check_rate_limit(request)

        if limit_result and "error" in limit_result:
            # Rate limit exceeded
            logger.warning(
                f"Rate limit exceeded for {self.limiter._get_client_ip(request)}: {limit_result['message']}"
            )

            headers = self.limiter._get_rate_limit_headers(limit_result)

            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": limit_result["message"],
                    "retry_after": limit_result.get("retry_after"),
                    "limit": limit_result.get("limit"),
                    "remaining": limit_result.get("remaining", 0),
                },
                headers=headers,
            )

        # Update global stats
        self.limiter.global_stats["total_requests"] += 1

        # Continue to next middleware
        response = await call_next(request)

        # Add rate limit headers to all responses
        if hasattr(response, "headers"):
            limit_info = await self.limiter.check_rate_limit(request)
            if limit_info:
                rate_headers = self.limiter._get_rate_limit_headers(limit_info)
                for key, value in rate_headers.items():
                    response.headers[key] = value

        return response


# Decorator for rate limiting individual endpoints
def rate_limit(
    limit: int = 100, window: int = 60, per_ip: bool = True, ip_limit: int = 50
):
    """Decorator to apply rate limiting to specific endpoints."""

    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Create rate limiter for this endpoint
            config = RateLimitConfig(
                enabled=True,
                default_limit=limit,
                window_seconds=window,
                ip_enabled=per_ip,
                ip_limit=ip_limit,
            )

            limiter = RateLimiter(config)
            await limiter.initialize()

            # Check rate limit
            limit_result = await limiter.check_rate_limit(request)

            if limit_result and "error" in limit_result:
                # Rate limit exceeded
                logger.warning(f"Rate limit exceeded for endpoint: {func.__name__}")

                headers = limiter._get_rate_limit_headers(limit_result)

                from fastapi import HTTPException

                raise HTTPException(
                    status_code=429, detail=limit_result["message"], headers=headers
                )

            # Update stats and continue
            limiter.global_stats["total_requests"] += 1
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


# Utility functions
async def get_rate_limiter_stats() -> Dict[str, Any]:
    """Get rate limiting statistics."""
    # This would need access to the global limiter instance
    # In a real implementation, you'd store the limiter instance globally
    return {
        "message": "Rate limiter stats not available in utility function",
        "timestamp": datetime.now().isoformat(),
    }


# Health check for rate limiting
async def rate_limiter_health_check() -> Dict[str, Any]:
    """Perform health check on rate limiting system."""
    try:
        # Create a test rate limiter
        config = RateLimitConfig(enabled=True)
        limiter = RateLimiter(config)
        await limiter.initialize()

        # Test basic functionality
        stats = limiter.get_stats()

        health_status = {
            "status": "healthy" if limiter._running else "stopped",
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        }

        await limiter.close()
        return health_status

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
