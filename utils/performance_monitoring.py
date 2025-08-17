#!/usr/bin/env python3
"""
🧠 Enhanced Performance Monitoring Utilities

Performance monitoring and analytics for the Consciousness WebUI with support for:
- Real-time metrics collection
- Performance alerts
- Resource usage tracking
- Response time monitoring
- User interaction analytics

Author: Dimensional AI
Version: 2.0.0
"""

import time
import psutil
import asyncio
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    response_time_ms: float
    active_connections: int
    queue_length: int
    generation_count: int
    error_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_mb': self.memory_mb,
            'response_time_ms': self.response_time_ms,
            'active_connections': self.active_connections,
            'queue_length': self.queue_length,
            'generation_count': self.generation_count,
            'error_count': self.error_count
        }

@dataclass
class AlertThresholds:
    """Alert threshold configuration."""
    cpu_usage: float = 80.0
    memory_usage: float = 80.0
    response_time: float = 2000.0
    error_rate: float = 5.0
    queue_length: int = 50

class PerformanceMonitor:
    """Enhanced performance monitoring system."""
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 alert_callback: Optional[Callable] = None):
        """Initialize performance monitor."""
        self.config = config or {}
        self.alert_callback = alert_callback
        self.thresholds = AlertThresholds(**self.config.get('alert_thresholds', {}))
        
        # Metrics storage
        self.metrics_history: deque = deque(maxlen=1000)
        self.user_interactions: deque = deque(maxlen=500)
        self.error_log: deque = deque(maxlen=100)
        
        # Current state tracking
        self.current_metrics = {}
        self.generation_count = 0
        self.error_count = 0
        self.active_connections = 0
        self.queue_length = 0
        self.start_time = time.time()
        
        # Performance tracking
        self.response_times: deque = deque(maxlen=100)
        self.generation_times: deque = deque(maxlen=100)
        
        # Monitoring control
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = self.config.get('monitoring_interval', 5.0)
        
        # Analytics
        self.session_stats = defaultdict(int)
        self.hourly_stats = defaultdict(lambda: defaultdict(int))
        
        logger.info("🔍 Performance monitor initialized")
    
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        if self.monitoring_active:
            logger.warning("Performance monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info(f"📊 Performance monitoring started (interval: {self.monitoring_interval}s)")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        
        logger.info("🛑 Performance monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._collect_metrics()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_metrics(self) -> None:
        """Collect current performance metrics."""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_mb = memory.used / (1024 * 1024)
            
            # Calculate average response time
            avg_response_time = (
                sum(self.response_times) / len(self.response_times) 
                if self.response_times else 0.0
            )
            
            # Create metrics object
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_mb=memory_mb,
                response_time_ms=avg_response_time,
                active_connections=self.active_connections,
                queue_length=self.queue_length,
                generation_count=self.generation_count,
                error_count=self.error_count
            )
            
            # Store metrics
            self.metrics_history.append(metrics)
            self.current_metrics = metrics.to_dict()
            
            # Check for alerts
            self._check_alerts(metrics)
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    def _check_alerts(self, metrics: PerformanceMetrics) -> None:
        """Check if any alert thresholds are exceeded."""
        alerts = []
        
        if metrics.cpu_percent > self.thresholds.cpu_usage:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > self.thresholds.memory_usage:
            alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")
        
        if metrics.response_time_ms > self.thresholds.response_time:
            alerts.append(f"Slow response time: {metrics.response_time_ms:.1f}ms")
        
        if metrics.queue_length > self.thresholds.queue_length:
            alerts.append(f"Long queue: {metrics.queue_length} items")
        
        # Calculate error rate
        total_generations = max(metrics.generation_count, 1)
        error_rate = (metrics.error_count / total_generations) * 100
        if error_rate > self.thresholds.error_rate:
            alerts.append(f"High error rate: {error_rate:.1f}%")
        
        # Send alerts
        if alerts and self.alert_callback:
            try:
                self.alert_callback(alerts, metrics)
            except Exception as e:
                logger.error(f"Error sending alerts: {e}")
    
    def record_generation_start(self) -> str:
        """Record start of text generation."""
        generation_id = f"gen_{int(time.time() * 1000)}"
        self.generation_count += 1
        self.session_stats['generations'] += 1
        
        # Update hourly stats
        hour_key = datetime.now().strftime('%Y-%m-%d-%H')
        self.hourly_stats[hour_key]['generations'] += 1
        
        return generation_id
    
    def record_generation_end(self, generation_id: str, 
                            success: bool = True, 
                            response_time: Optional[float] = None) -> None:
        """Record end of text generation."""
        if response_time:
            self.response_times.append(response_time)
            self.generation_times.append(response_time)
        
        if not success:
            self.error_count += 1
            self.session_stats['errors'] += 1
            hour_key = datetime.now().strftime('%Y-%m-%d-%H')
            self.hourly_stats[hour_key]['errors'] += 1
    
    def record_user_interaction(self, interaction_type: str, data: Dict[str, Any]) -> None:
        """Record user interaction for analytics."""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'type': interaction_type,
            'data': data
        }
        
        self.user_interactions.append(interaction)
        self.session_stats['interactions'] += 1
        
        # Update hourly stats
        hour_key = datetime.now().strftime('%Y-%m-%d-%H')
        self.hourly_stats[hour_key]['interactions'] += 1
    
    def record_error(self, error_type: str, error_message: str, 
                    context: Optional[Dict[str, Any]] = None) -> None:
        """Record error for monitoring."""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': error_message,
            'context': context or {}
        }
        
        self.error_log.append(error_entry)
        self.error_count += 1
    
    def update_connection_count(self, count: int) -> None:
        """Update active connection count."""
        self.active_connections = count
    
    def update_queue_length(self, length: int) -> None:
        """Update queue length."""
        self.queue_length = length
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.current_metrics.copy()
    
    def get_metrics_history(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get metrics history for specified minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        return [
            metrics.to_dict() for metrics in self.metrics_history
            if metrics.timestamp >= cutoff_time
        ]
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        uptime = time.time() - self.start_time
        
        return {
            'uptime_seconds': uptime,
            'uptime_formatted': str(timedelta(seconds=int(uptime))),
            'total_generations': self.generation_count,
            'total_errors': self.error_count,
            'total_interactions': self.session_stats['interactions'],
            'success_rate': (
                ((self.generation_count - self.error_count) / max(self.generation_count, 1)) * 100
            ),
            'avg_response_time': (
                sum(self.response_times) / len(self.response_times)
                if self.response_times else 0.0
            ),
            'current_connections': self.active_connections,
            'current_queue_length': self.queue_length
        }
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary."""
        session_stats = self.get_session_stats()
        
        # Recent performance trends
        recent_metrics = self.get_metrics_history(30)  # Last 30 minutes
        
        cpu_trend = [m['cpu_percent'] for m in recent_metrics] if recent_metrics else []
        memory_trend = [m['memory_percent'] for m in recent_metrics] if recent_metrics else []
        response_trend = [m['response_time_ms'] for m in recent_metrics] if recent_metrics else []
        
        return {
            'session': session_stats,
            'trends': {
                'cpu_average': sum(cpu_trend) / len(cpu_trend) if cpu_trend else 0,
                'memory_average': sum(memory_trend) / len(memory_trend) if memory_trend else 0,
                'response_average': sum(response_trend) / len(response_trend) if response_trend else 0,
                'cpu_peak': max(cpu_trend) if cpu_trend else 0,
                'memory_peak': max(memory_trend) if memory_trend else 0,
                'response_peak': max(response_trend) if response_trend else 0
            },
            'hourly_stats': dict(self.hourly_stats),
            'recent_errors': list(self.error_log)[-10:]  # Last 10 errors
        }
    
    def export_metrics(self, filepath: str, format: str = 'json') -> None:
        """Export metrics to file."""
        try:
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'session_stats': self.get_session_stats(),
                'analytics_summary': self.get_analytics_summary(),
                'full_metrics_history': [m.to_dict() for m in self.metrics_history],
                'user_interactions': list(self.user_interactions),
                'error_log': list(self.error_log)
            }
            
            filepath = Path(filepath)
            
            if format.lower() == 'json':
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"📊 Metrics exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            raise

# Global monitor instance
_monitor_instance = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = PerformanceMonitor()
    return _monitor_instance

def initialize_monitoring(config: Optional[Dict[str, Any]] = None,
                        alert_callback: Optional[Callable] = None) -> PerformanceMonitor:
    """Initialize global performance monitoring."""
    global _monitor_instance
    _monitor_instance = PerformanceMonitor(config, alert_callback)
    _monitor_instance.start_monitoring()
    return _monitor_instance

# Context manager for timing operations
class TimingContext:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, monitor: Optional[PerformanceMonitor] = None):
        self.operation_name = operation_name
        self.monitor = monitor or get_performance_monitor()
        self.start_time = None
        self.generation_id = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.generation_id = self.monitor.record_generation_start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000  # Convert to ms
        success = exc_type is None
        
        self.monitor.record_generation_end(
            self.generation_id, 
            success=success, 
            response_time=duration
        )
        
        if not success:
            self.monitor.record_error(
                error_type=exc_type.__name__ if exc_type else "Unknown",
                error_message=str(exc_val) if exc_val else "Unknown error",
                context={'operation': self.operation_name}
            )

def time_operation(operation_name: str):
    """Decorator for timing operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with TimingContext(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Export utilities
__all__ = [
    'PerformanceMonitor',
    'PerformanceMetrics',
    'AlertThresholds',
    'TimingContext',
    'get_performance_monitor',
    'initialize_monitoring',
    'time_operation'
]
