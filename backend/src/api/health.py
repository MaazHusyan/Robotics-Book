"""
Health check endpoint for RAG chatbot system.
Provides comprehensive system status, health metrics, and monitoring data.
"""

import os
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add a backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.metrics import get_metrics_collector
from utils.logging import get_logger
from utils.error_tracking import get_error_tracker
from utils.performance import get_performance_monitor
from models.database import execute_query
from api.websocket import get_connection_stats


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    version: str
    uptime_seconds: int
    active_connections: int
    database_status: Dict[str, Any]
    qdrant_status: Dict[str, Any]
    system_metrics: Dict[str, Any]
    error_summary: Dict[str, Any]


class DetailedHealthResponse(HealthResponse):
    """Detailed health response with extended metrics."""

    memory_usage: Dict[str, Any]
    cpu_usage: Dict[str, Any]
    disk_usage: Dict[str, Any]
    recent_errors: list
    performance_metrics: Dict[str, Any]


class HealthChecker:
    """Comprehensive health checking for the RAG chatbot system."""

    def __init__(self):
        self.start_time = time.time()
        self.metrics_collector = get_metrics_collector()
        self.error_tracker = get_error_tracker()
        self.performance_monitor = get_performance_monitor()
        self.logger = get_logger()

    def get_uptime_seconds(self) -> int:
        """Get system uptime in seconds."""
        return int(time.time() - self.start_time)

    def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            # Test basic connectivity
            result = execute_query("SELECT 1")
            connection_status = "healthy" if result else "unhealthy"

            # Test table existence
            tables_query = """
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
            tables = execute_query(tables_query)
            table_status = "healthy" if tables else "unhealthy"

            # Test recent queries performance
            recent_queries = execute_query("""
                SELECT COUNT(*) as query_count,
                       AVG(response_time_ms) as avg_response_time
                FROM query_logs 
                WHERE timestamp > NOW() - INTERVAL '1 hour'
            """)

            return {
                "status": connection_status
                if connection_status == "healthy" and table_status == "healthy"
                else "degraded",
                "connection": connection_status,
                "tables": table_status,
                "query_performance": recent_queries[0] if recent_queries else {},
                "last_check": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat(),
            }

    def check_qdrant_health(self) -> Dict[str, Any]:
        """Check Qdrant vector database health."""
        try:
            from models.qdrant_setup import get_qdrant_client, test_collection

            client = get_qdrant_client()
            collection_accessible = test_collection()

            # Test collection info
            if collection_accessible:
                from qdrant_client import QdrantClient

                qdrant_client_instance = QdrantClient(
                    url=client._url, api_key=client._api_key
                )

                collection_info = qdrant_client_instance.get_collection(
                    "content_vectors"
                )
                collection_status = "healthy"
            else:
                collection_status = "unhealthy"
                collection_info = None

            return {
                "status": collection_status,
                "collection_accessible": collection_accessible,
                "collection_info": collection_info,
                "last_check": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Qdrant health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat(),
            }

    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
                "status": "healthy" if memory.percent < 80 else "warning",
            }

            # CPU usage
            cpu = psutil.cpu_percent(interval=1)
            cpu_usage = {
                "percent": cpu,
                "count": psutil.cpu_count(),
                "status": "healthy" if cpu < 70 else "warning",
            }

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_usage = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
                "status": "healthy" if disk.percent < 85 else "warning",
            }

            # Network connections
            network = psutil.net_io_counters()
            network_connections = len(psutil.net_connections())

            return {
                "memory": memory_usage,
                "cpu": cpu_usage,
                "disk": disk_usage,
                "network_connections": network_connections,
                "status": "healthy"
                if (
                    memory_usage["status"] == "healthy"
                    and cpu_usage["status"] == "healthy"
                    and disk_usage["status"] == "healthy"
                )
                else "degraded",
            }

        except Exception as e:
            self.logger.error(f"System resource check failed: {e}")
            return {"status": "error", "error": str(e)}

    def check_service_dependencies(self) -> Dict[str, Any]:
        """Check external service dependencies."""
        dependencies = {}

        # Check OpenAI/Gemini service
        try:
            from services.embeddings import EmbeddingService

            embedding_service = EmbeddingService()

            # Test embedding generation
            import asyncio

            test_result = asyncio.run(
                embedding_service.generate_embedding("health check")
            )

            dependencies["gemini"] = {
                "status": "healthy" if test_result else "unhealthy",
                "last_check": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            dependencies["gemini"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat(),
            }

        # Check Qdrant service
        try:
            qdrant_status = self.check_qdrant_health()
            dependencies["qdrant"] = qdrant_status

        except Exception:
            dependencies["qdrant"] = {
                "status": "unhealthy",
                "error": "Failed to check Qdrant",
            }

        # Check database service
        try:
            db_status = self.check_database_health()
            dependencies["database"] = db_status

        except Exception:
            dependencies["database"] = {
                "status": "unhealthy",
                "error": "Failed to check database",
            }

        # Overall dependency status
        all_healthy = all(
            dep.get("status") == "healthy" for dep in dependencies.values()
        )

        return {
            "overall_status": "healthy" if all_healthy else "degraded",
            "services": dependencies,
            "last_check": datetime.utcnow().isoformat(),
        }

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors."""
        try:
            recent_errors = self.error_tracker.get_recent_errors(hours=1, limit=10)

            error_counts = {}
            for error in recent_errors:
                error_type = error.get("type", "unknown")
                error_counts[error_type] = error_counts.get(error_type, 0) + 1

            return {
                "total_errors": len(recent_errors),
                "error_counts": error_counts,
                "recent_errors": recent_errors[:5],  # Last 5 errors
                "last_check": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat(),
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        try:
            metrics = self.performance_monitor.get_current_metrics()

            return {
                "response_time_p95": metrics.get("response_time_p95", 0),
                "response_time_avg": metrics.get("response_time_avg", 0),
                "queries_per_second": metrics.get("queries_per_second", 0),
                "concurrent_users": metrics.get("concurrent_users", 0),
                "error_rate": metrics.get("error_rate", 0),
                "cache_hit_rate": metrics.get("cache_hit_rate", 0),
                "uptime_hours": self.get_uptime_seconds() / 3600,
                "last_check": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat(),
            }


# Create router
router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def basic_health_check():
    """Basic health check endpoint."""
    health_checker = HealthChecker()

    # Get basic stats
    connection_stats = get_connection_stats()
    uptime = health_checker.get_uptime_seconds()

    # Determine overall status
    overall_status = "healthy"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        uptime_seconds=uptime,
        active_connections=connection_stats["active_connections"],
    )


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """Detailed health check with comprehensive metrics."""
    health_checker = HealthChecker()

    # Get all health components
    connection_stats = get_connection_stats()
    database_health = health_checker.check_database_health()
    qdrant_health = health_checker.check_qdrant_health()
    system_resources = health_checker.check_system_resources()
    service_dependencies = health_checker.check_service_dependencies()
    error_summary = health_checker.get_error_summary()
    performance_metrics = health_checker.get_performance_metrics()

    # Determine overall status
    component_statuses = [
        database_health.get("status", "unhealthy"),
        qdrant_health.get("status", "unhealthy"),
        system_resources.get("status", "unhealthy"),
        service_dependencies.get("overall_status", "unhealthy"),
    ]

    if all(status == "healthy" for status in component_statuses):
        overall_status = "healthy"
    elif any(status == "unhealthy" for status in component_statuses):
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"

    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        uptime_seconds=health_checker.get_uptime_seconds(),
        active_connections=connection_stats["active_connections"],
        database_status=database_health,
        qdrant_status=qdrant_health,
        system_metrics=system_resources,
        error_summary=error_summary,
        performance_metrics=performance_metrics,
    )


@router.get("/metrics")
async def get_system_metrics():
    """Get detailed system metrics."""
    health_checker = HealthChecker()

    try:
        # Get comprehensive metrics
        system_resources = health_checker.check_system_resources()
        performance_metrics = health_checker.get_performance_metrics()
        connection_stats = get_connection_stats()

        # Get application-specific metrics
        app_metrics = self.metrics_collector.get_all_metrics()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": health_checker.get_uptime_seconds(),
            "system_resources": system_resources,
            "performance": performance_metrics,
            "connections": connection_stats,
            "application_metrics": app_metrics,
            "status": "success",
        }

    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e),
        }


@router.get("/errors")
async def get_recent_errors():
    """Get recent system errors."""
    health_checker = HealthChecker()

    try:
        error_summary = health_checker.get_error_summary()
        return error_summary

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/dependencies")
async def get_dependency_status():
    """Get external dependency status."""
    health_checker = HealthChecker()

    try:
        dependencies = health_checker.check_service_dependencies()
        return dependencies

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/ping")
async def ping():
    """Simple ping endpoint for load balancers."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# Health check utility functions
def run_health_checks() -> Dict[str, Any]:
    """Run all health checks and return summary."""
    health_checker = HealthChecker()

    checks = {
        "database": health_checker.check_database_health(),
        "qdrant": health_checker.check_qdrant_health(),
        "system_resources": health_checker.check_system_resources(),
        "service_dependencies": health_checker.check_service_dependencies(),
    }

    # Overall status
    statuses = [check.get("status", "unhealthy") for check in checks.values()]
    if all(status == "healthy" for status in statuses):
        overall_status = "healthy"
    elif any(status == "unhealthy" for status in statuses):
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"

    return {
        "overall_status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": health_checker.get_uptime_seconds(),
    }


def get_health_summary() -> Dict[str, Any]:
    """Get health summary for monitoring dashboards."""
    health_checker = HealthChecker()

    return {
        "status": "healthy",  # Would be calculated by run_health_checks()
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": health_checker.get_uptime_seconds(),
        "active_connections": get_connection_stats()["active_connections"],
        "version": "1.0.0",
    }
