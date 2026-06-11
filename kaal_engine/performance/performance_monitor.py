"""
Performance Monitoring System for Brahmakaal API
Real-time performance tracking, metrics collection, and alerting
"""

import time
import asyncio
import statistics
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field
import logging

import psutil


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    endpoint: str
    start_time: float
    end_time: float
    duration: float
    status: str
    cache_hit: bool = False
    error: Optional[str] = None
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    concurrent_requests: int = 0


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.
    Tracks response times, resource usage, and provides real-time analytics.
    """
    
    def __init__(self, max_metrics_history: int = 10000):
        self.max_metrics_history = max_metrics_history
        self.metrics_history: deque = deque(maxlen=max_metrics_history)
        self.endpoint_stats: Dict[str, Dict] = defaultdict(self._default_endpoint_stats)
        self.active_requests: Dict[str, float] = {}
        self.concurrent_requests = 0
        self.logger = logging.getLogger(__name__)
        
        # Performance thresholds
        self.thresholds = {
            'response_time_slow': 2.0,      # 2 seconds
            'response_time_critical': 5.0,  # 5 seconds
            'memory_warning': 80.0,         # 80% memory usage
            'cpu_warning': 80.0,           # 80% CPU usage
            'concurrent_requests_max': 100  # 100 concurrent requests
        }
        
        # Start background monitoring
        self._start_system_monitoring()
    
    def _default_endpoint_stats(self) -> Dict:
        """Default statistics structure for endpoints."""
        return {
            'total_requests': 0,
            'total_duration': 0.0,
            'min_duration': float('inf'),
            'max_duration': 0.0,
            'avg_duration': 0.0,
            'success_count': 0,
            'error_count': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'recent_durations': deque(maxlen=100),  # Last 100 requests
            'error_types': defaultdict(int)
        }
    
    def start_request(self, endpoint: str, request_id: str) -> str:
        """Start tracking a request."""
        start_time = time.time()
        self.active_requests[request_id] = start_time
        self.concurrent_requests += 1
        
        self.logger.debug(f"Started tracking request {request_id} for {endpoint}")
        return request_id
    
    def end_request(self, endpoint: str, request_id: str, status: str = "success", 
                   error: Optional[str] = None, cache_hit: bool = False) -> PerformanceMetrics:
        """End tracking a request and record metrics."""
        
        end_time = time.time()
        start_time = self.active_requests.pop(request_id, end_time)
        duration = end_time - start_time
        self.concurrent_requests = max(0, self.concurrent_requests - 1)
        
        # Get current system metrics
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent()
        
        # Create metrics object
        metrics = PerformanceMetrics(
            endpoint=endpoint,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            status=status,
            cache_hit=cache_hit,
            error=error,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            concurrent_requests=self.concurrent_requests
        )
        
        # Store metrics
        self.metrics_history.append(metrics)
        self._update_endpoint_stats(metrics)
        
        # Check for performance issues
        self._check_performance_alerts(metrics)
        
        self.logger.debug(f"Completed tracking request {request_id} for {endpoint} ({duration:.3f}s)")
        return metrics
    
    def _update_endpoint_stats(self, metrics: PerformanceMetrics):
        """Update endpoint-specific statistics."""
        stats = self.endpoint_stats[metrics.endpoint]
        
        stats['total_requests'] += 1
        stats['total_duration'] += metrics.duration
        stats['min_duration'] = min(stats['min_duration'], metrics.duration)
        stats['max_duration'] = max(stats['max_duration'], metrics.duration)
        stats['avg_duration'] = stats['total_duration'] / stats['total_requests']
        stats['recent_durations'].append(metrics.duration)
        
        if metrics.status == "success":
            stats['success_count'] += 1
        else:
            stats['error_count'] += 1
            if metrics.error:
                stats['error_types'][metrics.error] += 1
        
        if metrics.cache_hit:
            stats['cache_hits'] += 1
        else:
            stats['cache_misses'] += 1
    
    def _check_performance_alerts(self, metrics: PerformanceMetrics):
        """Check for performance issues and log alerts."""
        
        # Response time alerts
        if metrics.duration > self.thresholds['response_time_critical']:
            self.logger.error(f"CRITICAL: {metrics.endpoint} took {metrics.duration:.2f}s")
        elif metrics.duration > self.thresholds['response_time_slow']:
            self.logger.warning(f"SLOW: {metrics.endpoint} took {metrics.duration:.2f}s")
        
        # Resource usage alerts
        if metrics.memory_usage > self.thresholds['memory_warning']:
            self.logger.warning(f"HIGH MEMORY: {metrics.memory_usage:.1f}% usage")
        
        if metrics.cpu_usage > self.thresholds['cpu_warning']:
            self.logger.warning(f"HIGH CPU: {metrics.cpu_usage:.1f}% usage")
        
        # Concurrent requests alert
        if metrics.concurrent_requests > self.thresholds['concurrent_requests_max']:
            self.logger.warning(f"HIGH CONCURRENCY: {metrics.concurrent_requests} concurrent requests")
    
    def get_endpoint_summary(self, endpoint: str) -> Dict[str, Any]:
        """Get performance summary for a specific endpoint."""
        if endpoint not in self.endpoint_stats:
            return {"error": f"No data for endpoint {endpoint}"}
        
        stats = self.endpoint_stats[endpoint]
        
        # Calculate percentiles from recent durations
        recent_durations = list(stats['recent_durations'])
        percentiles = {}
        if recent_durations:
            percentiles = {
                'p50': statistics.median(recent_durations),
                'p95': statistics.quantiles(recent_durations, n=20)[18] if len(recent_durations) >= 20 else max(recent_durations),
                'p99': statistics.quantiles(recent_durations, n=100)[98] if len(recent_durations) >= 100 else max(recent_durations)
            }
        
        # Calculate rates
        total_requests = stats['total_requests']
        success_rate = (stats['success_count'] / total_requests * 100) if total_requests > 0 else 0
        cache_hit_rate = (stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses']) * 100) if (stats['cache_hits'] + stats['cache_misses']) > 0 else 0
        
        return {
            "endpoint": endpoint,
            "total_requests": total_requests,
            "success_rate_percentage": round(success_rate, 2),
            "cache_hit_rate_percentage": round(cache_hit_rate, 2),
            "response_times": {
                "average_ms": round(stats['avg_duration'] * 1000, 2),
                "min_ms": round(stats['min_duration'] * 1000, 2),
                "max_ms": round(stats['max_duration'] * 1000, 2),
                "percentiles_ms": {k: round(v * 1000, 2) for k, v in percentiles.items()}
            },
            "error_breakdown": dict(stats['error_types']),
            "performance_grade": self._calculate_performance_grade(stats)
        }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get overall system performance summary."""
        
        # Recent metrics (last 5 minutes)
        recent_cutoff = time.time() - 300
        recent_metrics = [m for m in self.metrics_history if m.end_time > recent_cutoff]
        
        # Calculate overall statistics
        total_requests = len(self.metrics_history)
        recent_requests = len(recent_metrics)
        
        if recent_metrics:
            avg_response_time = statistics.mean([m.duration for m in recent_metrics])
            success_rate = len([m for m in recent_metrics if m.status == "success"]) / recent_requests * 100
            cache_hit_rate = len([m for m in recent_metrics if m.cache_hit]) / recent_requests * 100
            avg_memory = statistics.mean([m.memory_usage for m in recent_metrics])
            avg_cpu = statistics.mean([m.cpu_usage for m in recent_metrics])
        else:
            avg_response_time = 0
            success_rate = 100
            cache_hit_rate = 0
            avg_memory = psutil.virtual_memory().percent
            avg_cpu = psutil.cpu_percent()
        
        # Endpoint performance rankings
        endpoint_rankings = []
        for endpoint, stats in self.endpoint_stats.items():
            if stats['total_requests'] > 0:
                endpoint_rankings.append({
                    "endpoint": endpoint,
                    "avg_response_ms": round(stats['avg_duration'] * 1000, 2),
                    "total_requests": stats['total_requests'],
                    "success_rate": round(stats['success_count'] / stats['total_requests'] * 100, 1)
                })
        
        endpoint_rankings.sort(key=lambda x: x['avg_response_ms'])
        
        return {
            "system_health": self._calculate_system_health(avg_response_time, success_rate, avg_memory, avg_cpu),
            "metrics_summary": {
                "total_requests_all_time": total_requests,
                "requests_last_5_minutes": recent_requests,
                "average_response_time_ms": round(avg_response_time * 1000, 2),
                "success_rate_percentage": round(success_rate, 2),
                "cache_hit_rate_percentage": round(cache_hit_rate, 2),
                "concurrent_requests": self.concurrent_requests
            },
            "resource_usage": {
                "memory_usage_percentage": round(avg_memory, 1),
                "cpu_usage_percentage": round(avg_cpu, 1),
                "active_requests": len(self.active_requests)
            },
            "endpoint_performance": endpoint_rankings[:10],  # Top 10 by speed
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_performance_grade(self, stats: Dict) -> str:
        """Calculate performance grade for an endpoint."""
        
        avg_duration_ms = stats['avg_duration'] * 1000
        success_rate = (stats['success_count'] / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0
        
        # Grade based on response time and success rate
        if avg_duration_ms < 100 and success_rate > 99:
            return "A+"
        elif avg_duration_ms < 200 and success_rate > 98:
            return "A"
        elif avg_duration_ms < 500 and success_rate > 95:
            return "B"
        elif avg_duration_ms < 1000 and success_rate > 90:
            return "C"
        elif avg_duration_ms < 2000 and success_rate > 85:
            return "D"
        else:
            return "F"
    
    def _calculate_system_health(self, avg_response_time: float, success_rate: float, 
                                memory_usage: float, cpu_usage: float) -> str:
        """Calculate overall system health status."""
        
        health_score = 0
        
        # Response time score (40% weight)
        if avg_response_time < 0.5:
            health_score += 40
        elif avg_response_time < 1.0:
            health_score += 30
        elif avg_response_time < 2.0:
            health_score += 20
        elif avg_response_time < 5.0:
            health_score += 10
        
        # Success rate score (30% weight)
        if success_rate > 99:
            health_score += 30
        elif success_rate > 95:
            health_score += 25
        elif success_rate > 90:
            health_score += 20
        elif success_rate > 85:
            health_score += 15
        elif success_rate > 80:
            health_score += 10
        
        # Memory usage score (15% weight)
        if memory_usage < 50:
            health_score += 15
        elif memory_usage < 70:
            health_score += 10
        elif memory_usage < 85:
            health_score += 5
        
        # CPU usage score (15% weight)
        if cpu_usage < 50:
            health_score += 15
        elif cpu_usage < 70:
            health_score += 10
        elif cpu_usage < 85:
            health_score += 5
        
        # Determine health status
        if health_score >= 90:
            return "Excellent"
        elif health_score >= 75:
            return "Good"
        elif health_score >= 60:
            return "Fair"
        elif health_score >= 40:
            return "Poor"
        else:
            return "Critical"
    
    def _start_system_monitoring(self):
        """Start background system monitoring."""
        def monitor_system():
            while True:
                try:
                    # Log system metrics every 60 seconds
                    time.sleep(60)
                    
                    memory_usage = psutil.virtual_memory().percent
                    cpu_usage = psutil.cpu_percent(interval=1)
                    
                    self.logger.info(f"System: {memory_usage:.1f}% memory, {cpu_usage:.1f}% CPU, "
                                   f"{self.concurrent_requests} active requests")
                    
                except Exception as e:
                    self.logger.error(f"System monitoring error: {e}")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        
        if format == "json":
            import json
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "system_summary": self.get_system_summary(),
                "endpoint_summaries": {
                    endpoint: self.get_endpoint_summary(endpoint)
                    for endpoint in self.endpoint_stats.keys()
                },
                "recent_metrics": [
                    {
                        "endpoint": m.endpoint,
                        "duration_ms": round(m.duration * 1000, 2),
                        "status": m.status,
                        "cache_hit": m.cache_hit,
                        "timestamp": datetime.fromtimestamp(m.end_time).isoformat()
                    }
                    for m in list(self.metrics_history)[-100:]  # Last 100 requests
                ]
            }
            return json.dumps(export_data, indent=2)
        
        elif format == "prometheus":
            # Export Prometheus metrics format
            metrics_lines = []
            
            for endpoint, stats in self.endpoint_stats.items():
                metrics_lines.append(f'brahmakaal_requests_total{{endpoint="{endpoint}"}} {stats["total_requests"]}')
                metrics_lines.append(f'brahmakaal_request_duration_avg{{endpoint="{endpoint}"}} {stats["avg_duration"]}')
                metrics_lines.append(f'brahmakaal_request_duration_max{{endpoint="{endpoint}"}} {stats["max_duration"]}')
                metrics_lines.append(f'brahmakaal_cache_hits_total{{endpoint="{endpoint}"}} {stats["cache_hits"]}')
                metrics_lines.append(f'brahmakaal_errors_total{{endpoint="{endpoint}"}} {stats["error_count"]}')
            
            return "\n".join(metrics_lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


# Decorator for automatic performance monitoring
def monitor_performance(endpoint: str):
    """Decorator to automatically monitor endpoint performance."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            request_id = f"{endpoint}_{time.time()}_{id(args)}"
            
            # Start monitoring
            monitor.start_request(endpoint, request_id)
            
            try:
                # Execute the function
                result = await func(*args, **kwargs)
                
                # Check if result indicates cache hit
                cache_hit = isinstance(result, dict) and result.get('_cache_info', {}).get('hit', False)
                
                # End monitoring with success
                monitor.end_request(endpoint, request_id, "success", cache_hit=cache_hit)
                
                return result
                
            except Exception as e:
                # End monitoring with error
                monitor.end_request(endpoint, request_id, "error", str(e))
                raise
        
        return wrapper
    return decorator 