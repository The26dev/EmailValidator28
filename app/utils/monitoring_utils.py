"""Monitoring utilities for resource usage and performance tracking."""
import logging
import psutil
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_resource_usage() -> Dict[str, Any]:
    """
    Get current system resource usage metrics.
    
    Returns:
        Dict containing CPU, memory, and I/O metrics
    """
    try:
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters()._asdict() if hasattr(psutil, 'disk_io_counters') else {},
            'network_io': psutil.net_io_counters()._asdict(),
            'timestamp': time.time()
        }
        return metrics
    except Exception as e:
        logger.error(f"Failed to get resource metrics: {e}")
        return {}

def check_performance_thresholds(metrics: Dict[str, Any]) -> bool:
    """
    Check if system metrics are within acceptable thresholds.
    
    Args:
        metrics: Dictionary of system metrics
    
    Returns:
        bool indicating if all metrics are within acceptable ranges
    """
    try:
        # Define thresholds
        CPU_THRESHOLD = 80.0  # percentage
        MEMORY_THRESHOLD = 85.0  # percentage
        
        # Check CPU usage
        if metrics.get('cpu_percent', 0) > CPU_THRESHOLD:
            logger.warning(f"CPU usage above threshold: {metrics['cpu_percent']}%")
            return False
            
        # Check memory usage
        if metrics.get('memory_percent', 0) > MEMORY_THRESHOLD:
            logger.warning(f"Memory usage above threshold: {metrics['memory_percent']}%")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Failed to check performance thresholds: {e}")
        return False

def log_performance_metrics(metrics: Dict[str, Any]) -> None:
    """
    Log current performance metrics for monitoring.
    
    Args:
        metrics: Dictionary of system metrics
    """
    try:
        logger.info(
            "Performance Metrics - "
            f"CPU: {metrics.get('cpu_percent', 0)}%, "
            f"Memory: {metrics.get('memory_percent', 0)}%, "
            f"Network IO: {metrics.get('network_io', {}).get('bytes_sent', 0)} bytes sent, "
            f"{metrics.get('network_io', {}).get('bytes_recv', 0)} bytes received"
        )
    except Exception as e:
        logger.error(f"Failed to log performance metrics: {e}")