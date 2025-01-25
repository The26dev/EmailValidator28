"""Performance metrics collection for the Email Validator Service."""

from typing import Dict, Optional
from ..utils.metrics import record_metric, timing_metric
from ..utils.logger import logger

def track_validation_performance(duration: float, success: bool, validation_type: str):
    """Track email validation performance metrics.
    
    Args:
        duration: Time taken for validation in seconds
        success: Whether validation was successful
        validation_type: Type of validation performed
    """
    try:
        tags = {
            "validation_type": validation_type,
            "status": "success" if success else "failure"
        }
        
        record_metric("validation.duration", duration, tags)
        record_metric("validation.count", 1, tags)
        
    except Exception as e:
        logger.error(f"Failed to record validation performance metrics: {str(e)}")
        logger.debug("Validation metrics details", extra={
            "duration": duration,
            "success": success,
            "validation_type": validation_type
        })

def track_system_resources():
    """Track system resource utilization metrics."""
    try:
        import psutil
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        record_metric("system.cpu.percent", cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        record_metric("system.memory.percent", memory.percent)
        record_metric("system.memory.used", memory.used)
        record_metric("system.memory.available", memory.available)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        record_metric("system.disk.percent", disk.percent)
        record_metric("system.disk.used", disk.used)
        record_metric("system.disk.free", disk.free)
        
    except Exception as e:
        logger.error(f"Failed to record system resource metrics: {str(e)}")
        
def track_api_latency(endpoint: str, duration: float, status_code: int):
    """Track API endpoint latency.
    
    Args:
        endpoint: API endpoint path
        duration: Request duration in seconds
        status_code: Response status code
    """
    try:
        tags = {
            "endpoint": endpoint,
            "status": str(status_code)[0] + "xx"  # Group by status class
        }
        
        record_metric("api.latency", duration, tags)
        
    except Exception as e:
        logger.error(f"Failed to record API latency metric: {str(e)}")
        logger.debug("API latency details", extra={
            "endpoint": endpoint,
            "duration": duration,
            "status_code": status_code
        })