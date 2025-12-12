"""
Performance monitoring utilities for RAG chatbot.
Provides metrics collection, performance tracking, and system health monitoring.
"""

import time
import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import psutil
import threading

from ..utils.config import get_config
from ..utils.errors import CacheError


logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric data point."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    type: str = "counter"  # counter, gauge, histogram, timer


@dataclass
class PerformanceConfig:
    """Configuration for performance monitoring."""
    enabled: bool = True
    collection_interval: float = 60.0  # 1 minute
    retention_period: timedelta = timedelta(hours=24)  # Keep 24 hours of data
    max_points_per_metric: int = 10000
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'response_time_p95': 2.0,  # 2 seconds
        'error_rate': 0.05,  # 5%
        'cache_hit_rate': 0.8,  # 80%
        'memory_usage': 0.9,  # 90%
        'cpu_usage': 0.9,  # 90%
    })
    system_monitoring: bool = True
    detailed_logging: bool = False


class MetricsCollector:
    """Collects and manages performance metrics."""
    
    def __init__(self, config: Optional[PerformanceConfig] = None):
        self.config = config or PerformanceConfig()
        self.metrics = defaultdict(lambda: deque(maxlen=self.config.max_points_per_metric))
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        self.gauges = defaultdict(float)
        self.alerts = []
        self.start_time = time.time()
        self._collection_task = None
        self._system_monitor_task = None
        self._running = False
        
    def _get_metric_key(self, name: str, tags: Dict[str, str]) -> str:
        """Generate consistent metric key."""
        if tags:
            tag_str = ",".join(f"{k}:{v}" for k, v in sorted(tags.items()))
            return f"{name}{{{tag_str}}}"
        return name
    
    def record_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None):
        """Record a counter metric."""
        key = self._get_metric_key(name, tags or {})
        self.counters[key] += value
        
        metric_point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            type="counter"
        )
        self.metrics[key].append(metric_point)
    
    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a gauge metric."""
        key = self._get_metric_key(name, tags or {})
        self.gauges[key] = value
        
        metric_point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            type="gauge"
        )
        self.metrics[key].append(metric_point)
    
    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record a timer metric."""
        key = self._get_metric_key(name, tags or {})
        
        metric_point = MetricPoint(
            name=name,
            value=duration,
            timestamp=datetime.now(),
            tags=tags or {},
            type="timer",
            unit="seconds"
        )
        self.metrics[key].append(metric_point)
        self.timers[key].append(duration)
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram metric."""
        key = self._get_metric_key(name, tags or {})
        
        metric_point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            type="histogram"
        )
        self.metrics[key].append(metric_point)
    
    def increment_counter(self, name: str, tags: Dict[str, str] = None):
        """Increment a counter metric by 1."""
        self.record_counter(name, 1.0, tags)
    
    def get_metric_stats(self, name: str, tags: Dict[str, str] = None, 
                       since: Optional[datetime] = None) -> Dict[str, Any]:
        """Get statistics for a specific metric."""
        key = self._get_metric_key(name, tags or {})
        
        if key not in self.metrics:
            return {'error': f'Metric {name} not found'}
        
        points = list(self.metrics[key])
        
        # Filter by time if specified
        if since:
            points = [p for p in points if p.timestamp >= since]
        else:
            points = points
        
        if not points:
            return {'error': 'No data points found'}
        
        # Calculate statistics based on metric type
        if points and points[0].type == "counter":
            values = [p.value for p in points]
            return {
                'count': len(values),
                'sum': sum(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'latest': points[-1].value if points else 0,
                'points_count': len(points)
            }
        
        elif points and points[0].type == "gauge":
            values = [p.value for p in points]
            return {
                'current': values[-1] if values else 0,
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'points_count': len(points)
            }
        
        elif points and points[0].type == "timer":
            durations = [p.value for p in points]
            return {
                'count': len(durations),
                'avg': sum(durations) / len(durations),
                'min': min(durations),
                'max': max(durations),
                'p50': self._percentile(durations, 50),
                'p95': self._percentile(durations, 95),
                'p99': self._percentile(durations, 99),
                'latest': durations[-1] if durations else 0,
                'points_count': len(points)
            }
        
        elif points and points[0].type == "histogram":
            values = [p.value for p in points]
            return {
                'count': len(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'p50': self._percentile(values, 50),
                'p95': self._percentile(values, 95),
                'p99': self._percentile(values, 99),
                'points_count': len(points)
            }
        
        return {'error': f'Unknown metric type: {points[0].type}'}
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        result = {}
        
        for key, points in self.metrics.items():
            if points:
                latest_point = points[-1]
                result[key] = {
                    'name': latest_point.name,
                    'current_value': latest_point.value,
                    'type': latest_point.type,
                    'unit': latest_point.unit,
                    'tags': latest_point.tags,
                    'timestamp': latest_point.timestamp.isoformat(),
                    'points_count': len(points)
                }
                
                # Add type-specific statistics
                if latest_point.type == "timer":
                    durations = [p.value for p in points]
                    result[key].update({
                        'avg_duration': sum(durations) / len(durations),
                        'min_duration': min(durations),
                        'max_duration': max(durations),
                        'p95_duration': self._percentile(durations, 95)
                    })
                elif latest_point.type == "counter":
                    values = [p.value for p in points]
                    result[key].update({
                        'total_count': sum(values),
                        'avg_count': sum(values) / len(values)
                    })
        
        return result
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        return self.alerts.copy()
    
    def clear_alerts(self):
        """Clear all active alerts."""
        self.alerts.clear()
    
    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff_time = datetime.now() - self.config.retention_period
        
        for key in list(self.metrics.keys()):
            # Keep only recent points
            self.metrics[key] = deque(
                (p for p in self.metrics[key] if p.timestamp >= cutoff_time),
                maxlen=self.config.max_points_per_metric
            )
    
    async def start_collection(self):
        """Start metrics collection."""
        if self._running:
            return
        
        self._running = True
        
        # Start periodic collection
        self._collection_task = asyncio.create_task(self._collection_loop())
        
        # Start system monitoring if enabled
        if self.config.system_monitoring:
            self._system_monitor_task = asyncio.create_task(self._system_monitor_loop())
        
        logger.info("Performance monitoring started")
    
    async def stop_collection(self):
        """Stop metrics collection."""
        self._running = False
        
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        
        if self._system_monitor_task:
            self._system_monitor_task.cancel()
            try:
                await self._system_monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Performance monitoring stopped")
    
    async def _collection_loop(self):
        """Periodic metrics collection and cleanup."""
        while self._running:
            try:
                await asyncio.sleep(self.config.collection_interval)
                self._cleanup_old_metrics()
                self._check_alert_conditions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
    
    async def _system_monitor_loop(self):
        """System resource monitoring loop."""
        while self._running:
            try:
                await asyncio.sleep(self.config.collection_interval)
                await self._collect_system_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in system monitor loop: {e}")
    
    async def _collect_system_metrics(self):
        """Collect system resource metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_gauge("system_cpu_usage", cpu_percent, {"unit": "percent"})
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.record_gauge("system_memory_usage", memory_percent, {"unit": "percent"})
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            self.record_gauge("system_disk_usage", disk_percent, {"unit": "percent"})
            
            # Network I/O
            network = psutil.net_io_counters()
            if network:
                bytes_sent = network.bytes_sent
                bytes_recv = network.bytes_recv
                self.record_counter("network_bytes_sent", bytes_sent)
                self.record_counter("network_bytes_recv", bytes_recv)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _check_alert_conditions(self):
        """Check for alert conditions and generate alerts."""
        current_time = datetime.now()
        
        # Check response time alert
        response_time_stats = self.get_metric_stats("response_time")
        if (response_time_stats.get('p95_duration', 0) > 
            self.config.alert_thresholds['response_time_p95']):
            
            alert = {
                'type': 'performance',
                'metric': 'response_time_p95',
                'threshold': self.config.alert_thresholds['response_time_p95'],
                'current_value': response_time_stats['p95_duration'],
                'timestamp': current_time.isoformat(),
                'message': f"P95 response time ({response_time_stats['p95_duration']:.2f}s) exceeds threshold ({self.config.alert_thresholds['response_time_p95']}s)"
            }
            self.alerts.append(alert)
            logger.warning(alert['message'])
        
        # Check error rate alert
        total_requests = sum(self.counters.values())
        if total_requests > 0:
            error_rate = self.counters.get('errors', 0) / total_requests
            if error_rate > self.config.alert_thresholds['error_rate']:
                
                alert = {
                    'type': 'error_rate',
                    'metric': 'error_rate',
                    'threshold': self.config.alert_thresholds['error_rate'],
                    'current_value': error_rate,
                    'timestamp': current_time.isoformat(),
                    'message': f"Error rate ({error_rate:.2%}) exceeds threshold ({self.config.alert_thresholds['error_rate']*100}%)"
                }
                self.alerts.append(alert)
                logger.warning(alert['message'])
        
        # Check cache hit rate alert
        cache_stats = self.get_metric_stats("cache_hit_rate")
        if (cache_stats.get('current_value', 0) < 
            self.config.alert_thresholds['cache_hit_rate']):
            
            alert = {
                'type': 'cache_performance',
                'metric': 'cache_hit_rate',
                'threshold': self.config.alert_thresholds['cache_hit_rate'],
                'current_value': cache_stats.get('current_value', 0),
                'timestamp': current_time.isoformat(),
                'message': f"Cache hit rate ({cache_stats.get('current_value', 0):.2%}) below threshold ({self.config.alert_thresholds['cache_hit_rate']*100}%)"
            }
            self.alerts.append(alert)
            logger.warning(alert['message'])
        
        # Check system resource alerts
        system_cpu = self.get_metric_stats("system_cpu_usage")
        if (system_cpu.get('current_value', 0) > 
            self.config.alert_thresholds['cpu_usage']):
            
            alert = {
                'type': 'system_resource',
                'metric': 'cpu_usage',
                'threshold': self.config.alert_thresholds['cpu_usage'],
                'current_value': system_cpu.get('current_value', 0),
                'timestamp': current_time.isoformat(),
                'message': f"CPU usage ({system_cpu.get('current_value', 0):.1f}%) exceeds threshold ({self.config.alert_thresholds['cpu_usage']*100}%)"
            }
            self.alerts.append(alert)
            logger.warning(alert['message'])
        
        # Keep only recent alerts (last 100)
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]


# Decorators for automatic metric recording
def timed_metric(name: str, tags: Dict[str, str] = None):
    """Decorator to automatically record timing of functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                # Get global metrics collector
                collector = get_metrics_collector()
                collector.record_timer(name, duration, tags)
        return wrapper
    return decorator


def counted_metric(name: str, tags: Dict[str, str] = None):
    """Decorator to automatically count function calls."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                # Get global metrics collector
                collector = get_metrics_collector()
                collector.increment_counter(name, tags)
                return result
            except Exception as e:
                # Record error on failure
                collector = get_metrics_collector()
                collector.increment_counter("errors", tags)
                collector.increment_counter(f"{name}_errors", tags)
                raise
        return wrapper
    return decorator


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _metrics_collector
    
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    
    return _metrics_collector


async def start_metrics_collection(config: Optional[PerformanceConfig] = None):
    """Start global metrics collection."""
    collector = get_metrics_collector()
    await collector.start_collection()


async def stop_metrics_collection():
    """Stop global metrics collection."""
    collector = get_metrics_collector()
    await collector.stop_collection()


def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary."""
    collector = get_metrics_collector()
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': time.time() - collector.start_time if collector.start_time > 0 else 0,
        'metrics': collector.get_all_metrics(),
        'alerts': collector.get_alerts(),
        'counters': dict(collector.counters),
        'system_info': {
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_total': psutil.disk_usage('/').total
        }
    }
    
    return summary


# Health check function
async def metrics_health_check() -> Dict[str, Any]:
    """Perform health check on metrics system."""
    try:
        collector = get_metrics_collector()
        
        health_status = {
            'status': 'healthy' if collector._running else 'stopped',
            'collection_active': collector._running,
            'metrics_count': len(collector.metrics),
            'alerts_count': len(collector.alerts),
            'last_collection': collector.metrics[list(collector.metrics.keys())[0][-1].timestamp.isoformat() if collector.metrics else None,
            'timestamp': datetime.now().isoformat()
        }
        
        return health_status
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }