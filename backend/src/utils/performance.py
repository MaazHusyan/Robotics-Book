"""
Performance monitoring for RAG chatbot system.
Provides real-time performance tracking and optimization recommendations.
"""

import os
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import deque, defaultdict
import asyncio

# Add a backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.logging import get_logger
from utils.metrics import get_metrics_collector
from utils.error_tracking import get_error_tracker


@dataclass
class PerformanceSnapshot:
    """Snapshot of system performance at a point in time."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    cpu_percent: float = field(default=0.0)
    memory_usage_mb: float = field(default=0.0)
    disk_usage_mb: float = field(default=0.0)
    active_connections: int = field(default=0)
    queries_per_second: float = field(default=0.0)
    avg_response_time_ms: float = field(default=0.0)
    error_rate_per_second: float = field(default=0.0)
    cache_hit_rate: float = field(default=0.0)
    uptime_seconds: int = field(default=0)
    system_load_index: float = field(default=0.0)  # 0-1 scale


@dataclass
class PerformanceAlert:
    """Performance alert definition."""
    alert_type: str
    severity: str  # info, warning, critical
    message: str
    threshold: float
    current_value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ResourceUsage:
    """Resource usage information."""
    cpu_percent: float
    memory_mb: float
    memory_available_mb: float
    disk_usage_mb: float
    disk_available_mb: float
    network_io: Dict[str, Any]
    active_threads: int


class PerformanceMonitor:
    """Real-time performance monitoring system."""
    
    def __init__(self, monitoring_interval: float = 5.0):
        self.logger = get_logger()
        self.metrics_collector = get_metrics_collector()
        self.error_tracker = get_error_tracker()
        
        self.monitoring = False
        self.monitoring_interval = monitoring_interval
        self.start_time = time.time()
        
        # Performance history
        self.performance_history: deque[PerformanceSnapshot] = deque(maxlen=1000)
        self.current_snapshot = None
        
        # Alert configuration
        self.alert_thresholds = {
            "response_time_p95": 2000.0,  # 2 seconds
            "response_time_avg": 1500.0,  # 1.5 seconds
            "error_rate": 0.05,  # 5% error rate
            "cache_hit_rate": 0.7,  # 70% cache hit rate
            "cpu_usage": 0.8,  # 80% CPU usage
            "memory_usage": 0.85,  # 85% memory usage
            "system_load_index": 0.7  # System load index
        }
        
        # Performance alerts
        self.active_alerts: List[PerformanceAlert] = []
        self.alert_cooldown = {}
        
        # Optimization recommendations
        self.optimization_cache = {}
        self.last_optimization_check = time.time()
    
    def start_monitoring(self):
        """Start performance monitoring."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.start_time = time.time()
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop)
        
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        if not self.monitoring:
            return
        
        self.monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
        
        if self.monitoring_task:
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Performance monitoring stopped")
    
    def get_current_snapshot(self) -> PerformanceSnapshot:
        """Get current performance snapshot."""
        if not self.monitoring:
            return PerformanceSnapshot()
        
        # Collect current metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get connection metrics from metrics collector
        all_metrics = self.metrics_collector.get_all_metrics()
        
        # Calculate queries per second
        uptime = time.time() - self.start_time
        queries_per_second = all_metrics.get("total_queries", 0) / max(uptime, 1)
        
        # Get recent performance metrics
        response_time_stats = self.metrics_collector.get_metric_summary("response_time", "1m")
        error_rate = all_metrics.get("error_rate", 0)
        cache_hit_rate = all_metrics.get("cache_hit_rate", 0)
        
        return PerformanceSnapshot(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_usage_mb=memory.used / (1024 * 1024),
            disk_usage_mb=disk.used / (1024 * 1024),
            active_connections=all_metrics.get("active_connections", 0),
            queries_per_second=queries_per_second,
            avg_response_time_ms=response_time_stats.get("avg_value", 0),
            error_rate_per_second=error_rate,
            cache_hit_rate=cache_hit_rate,
            uptime_seconds=int(uptime),
            system_load_index=self._calculate_system_load_index(cpu_percent, memory_usage_mb, disk_usage_mb, queries_per_second)
        )
    
    def _calculate_system_load_index(self, cpu_percent: float, memory_mb: float, 
                              disk_usage_mb: float, queries_per_second: float) -> float:
        """Calculate system load index (0-1 scale)."""
        # Weight factors for different resource types
        cpu_weight = 0.4
        memory_weight = 0.3
        disk_weight = 0.2
        queries_weight = 0.1
        
        # Calculate individual load indices
        cpu_load = min(cpu_percent / 100.0, 1.0) * cpu_weight
        memory_load = min(memory_mb / 4096.0, 1.0) * memory_weight  # Assume 4GB max memory
        disk_load = min(disk_usage_mb / 102400.0, 1.0) * disk_weight  # Assume 100GB max disk
        query_load = min(queries_per_second / 100.0, 1.0) * queries_weight
        
        # Combined system load index
        system_load = (cpu_load + memory_load + disk_load + query_load) / (
            cpu_weight + memory_weight + disk_weight + queries_weight
        )
        
        return system_load
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                # Collect system metrics
                snapshot = self.get_current_snapshot()
                self.current_snapshot = snapshot
                self.performance_history.append(snapshot)
                
                # Keep only recent snapshots
                if len(self.performance_history) > 1000:
                    self.performance_history.popleft()
                
                # Check for performance alerts
                self._check_performance_alerts(snapshot)
                
                # Check for optimization opportunities
                if time.time() - self.last_optimization_check > 300:  # Every 5 minutes
                    self._check_optimization_opportunities()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                break
    
    def _check_performance_alerts(self, snapshot: PerformanceSnapshot):
        """Check for performance alerts and generate recommendations."""
        alerts = []
        
        # Check response time alerts
        if snapshot.avg_response_time_ms > self.alert_thresholds["response_time_p95"]:
            alerts.append(PerformanceAlert(
                alert_type="performance",
                severity="critical",
                message=f"P95 response time ({snapshot.avg_response_time_ms:.2f}ms) exceeds threshold ({self.alert_thresholds['response_time_p95']}ms)",
                threshold=self.alert_thresholds["response_time_p95"],
                current_value=snapshot.avg_response_time_ms,
                timestamp=snapshot.timestamp,
                recommendations=[
                    "Optimize database queries",
                    "Implement response caching",
                    "Reduce concurrent query processing"
                ]
            ))
        
        # Check error rate alerts
        if snapshot.error_rate_per_second > self.alert_thresholds["error_rate"]:
            alerts.append(PerformanceAlert(
                alert_type="performance",
                severity="warning",
                message=f"Error rate ({snapshot.error_rate_per_second:.2%}) exceeds threshold ({self.alert_thresholds['error_rate']*100}%)",
                threshold=self.alert_thresholds["error_rate"],
                current_value=snapshot.error_rate_per_second,
                timestamp=snapshot.timestamp,
                recommendations=[
                    "Improve input validation",
                    "Add more comprehensive error handling",
                    "Review recent error patterns"
                ]
            ))
        
        # Check cache hit rate alerts
        if snapshot.cache_hit_rate < self.alert_thresholds["cache_hit_rate"]:
            alerts.append(PerformanceAlert(
                alert_type="performance",
                severity="warning",
                message=f"Cache hit rate ({snapshot.cache_hit_rate:.1%}) below threshold ({self.alert_thresholds['cache_hit_rate']*100}%)",
                threshold=self.alert_thresholds["cache_hit_rate"],
                current_value=snapshot.cache_hit_rate,
                timestamp=snapshot.timestamp,
                recommendations=[
                    "Review caching strategy",
                    "Increase cache TTL for frequently accessed content",
                    "Implement cache warming"
                ]
            ))
        
        # Check system resource alerts
        if snapshot.cpu_percent > self.alert_thresholds["cpu_usage"]:
            alerts.append(PerformanceAlert(
                alert_type="system_resource",
                severity="critical",
                message=f"CPU usage ({snapshot.cpu_percent:.1f}%) exceeds threshold ({self.alert_thresholds['cpu_usage']*100}%)",
                threshold=self.alert_thresholds["cpu_usage"],
                current_value=snapshot.cpu_percent,
                timestamp=snapshot.timestamp,
                recommendations=[
                    "Scale horizontally or optimize queries",
                    "Implement query queuing",
                    "Add CPU-intensive task offloading"
                ]
            ))
        
        if snapshot.memory_usage_mb > self.alert_thresholds["memory_usage"]:
            alerts.append(PerformanceAlert(
                alert_type="system_resource",
                severity="warning",
                message=f"Memory usage ({snapshot.memory_usage_mb:.1f}MB) exceeds threshold ({self.alert_thresholds['memory_usage']*1024}MB)",
                threshold=self.alert_thresholds["memory_usage"],
                current_value=snapshot.memory_usage_mb,
                timestamp=snapshot.timestamp,
                recommendations=[
                    "Optimize memory usage",
                    "Implement memory pooling",
                    "Review for memory leaks"
                ]
            ))
        
        # Add alerts to active list
        for alert in alerts:
            self._add_alert(alert)
        
        return alerts
    
    def _add_alert(self, alert: PerformanceAlert):
        """Add alert to active list with cooldown."""
        alert_key = f"{alert.alert_type}_{alert.severity}"
        
        # Check cooldown
        current_time = time.time()
        if alert_key in self.alert_cooldown:
            cooldown_time = self.alert_cooldown[alert_key]
            if current_time - cooldown_time < 60:  # 1 minute cooldown
                return  # Still in cooldown
        
        # Add alert
        self.active_alerts.append(alert)
        self.alert_cooldown[alert_key] = = current_time
        
        self.logger.warning(f"Performance alert: {alert.message}")
    
    def _check_optimization_opportunities(self):
        """Check for optimization opportunities."""
        # Get recent performance metrics
        recent_metrics = list(self.performance_history)[-10:]  # Last 10 snapshots
        
        if len(recent_metrics) < 5:
            return  # Not enough data
        
        # Analyze trends
        avg_response_times = [m.avg_response_time_ms for m in recent_metrics]
        avg_cpu_usage = [m.cpu_percent for m in recent_metrics]
        
        # Check for consistently slow responses
        slow_responses = [
            m for m in recent_metrics
            if m.avg_response_time_ms > 2000  # > 2 seconds
        ]
        
        if slow_responses:
            recommendations = [
                "Investigate slow query processing",
                "Check for blocking operations",
                "Optimize database queries",
                "Review embedding generation performance"
            ]
        else:
            # Check for high CPU usage
            high_cpu_usage = [
                m for m in recent_metrics if m.cpu_percent > 80
            ]
            
            if high_cpu_usage:
                recommendations = [
                    "Profile CPU-intensive operations",
                    "Optimize algorithms",
                    "Consider query batching",
                    "Implement result streaming"
                ]
        
        # Store recommendations
        self.optimization_cache["recommendations"] = recommendations
    
    def get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations."""
        return self.optimization_cache.get("recommendations", [])
    
    def get_alert_history(self, limit: int = 50) -> List[PerformanceAlert]:
        """Get recent alert history."""
        return list(self.active_alerts)[-limit:]
    
    def clear_alert_history(self):
        """Clear alert history."""
        self.active_alerts.clear()
        self.alert_cooldown.clear()
        self.logger.info("Alert history cleared")


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


# Convenience functions for other modules
def record_performance_snapshot():
    """Record current performance snapshot."""
    monitor = get_performance_monitor()
    snapshot = monitor.get_current_snapshot()
    
    # Record with metrics collector
    metrics_collector = get_metrics_collector()
    metrics_collector.record_event(
        event_type="system",
        metric_name="performance_snapshot",
        value=1.0,
        tags={
            "cpu_percent": snapshot.cpu_percent,
            "memory_usage_mb": snapshot.memory_usage_mb,
            "queries_per_second": snapshot.queries_per_second,
            "avg_response_time_ms": snapshot.avg_response_time_ms,
            "system_load_index": snapshot.system_load_index
        }
    )


def get_performance_alerts() -> List[PerformanceAlert]:
    """Get active performance alerts."""
    monitor = get_performance_monitor()
    return monitor.get_alert_history()


def get_performance_history(self, hours: int = 24) -> List[PerformanceSnapshot]:
    """Get performance history for specified hours."""
    monitor = get_performance_monitor()
    
    # Filter history by time window
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    filtered_history = [
        snapshot for snapshot in monitor.performance_history
        if snapshot.timestamp >= cutoff_time
    ]
    
    return filtered_history


def check_performance_health() -> Dict[str, Any]:
    """Check overall performance health status."""
    monitor = get_performance_monitor()
    
    if not monitor.monitoring:
        return {"status": "stopped", "message": "Performance monitoring is not active"}
    
    # Get current snapshot
    snapshot = monitor.get_current_snapshot()
    
    # Determine health status
    health_status = "healthy"
    
    # Check for critical issues
    if (snapshot.cpu_percent > 90 or 
            snapshot.memory_usage_mb > 90 or 
            snapshot.system_load_index > 0.8):
        health_status = "critical"
    elif (snapshot.cpu_percent > 80 or 
              snapshot.memory_usage_mb > 80 or 
              snapshot.system_load_index > 0.7):
        health_status = "warning"
    elif (snapshot.avg_response_time_ms > 3000 or 
              snapshot.error_rate_per_second > 0.1):
        health_status = "degraded"
    
    return {
        "status": health_status,
        "snapshot": snapshot,
        "timestamp": snapshot.timestamp,
        "recommendations": monitor.get_performance_recommendations()
    }


def start_performance_monitoring(monitoring_interval: float = 5.0):
    """Start performance monitoring with custom interval."""
    monitor = get_performance_monitor()
    monitor.start_monitoring(monitoring_interval)


def stop_performance_monitoring():
    """Stop performance monitoring."""
    monitor = get_performance_monitor()
    monitor.stop_monitoring()