"""Helper functions for metrics collection and processing."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from .logger import logger
from .metrics import record_metric, increment_counter

def format_error_context(
    error_type: str,
    message: str,
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format error context for consistent logging and metrics.
    
    Args:
        error_type: Type of error
        message: Error message
        additional_context: Additional error context
        
    Returns:
        Dictionary containing formatted error context
    """
    context = {
        "error_type": error_type,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if additional_context:
        context.update({k: str(v) for k, v in additional_context.items()})
        
    return context

def track_batch_metrics(
    operation: str,
    success_count: int,
    failure_count: int,
    duration: float,
    additional_tags: Optional[Dict[str, str]] = None
) -> None:
    """Track metrics for batch operations.
    
    Args:
        operation: Name of the batch operation
        success_count: Number of successful items
        failure_count: Number of failed items
        duration: Operation duration in seconds
        additional_tags: Additional metric tags
    """
    try:
        tags = {"operation": operation}
        if additional_tags:
            tags.update(additional_tags)
            
        total = success_count + failure_count
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        metrics = {
            f"{operation}.success_count": success_count,
            f"{operation}.failure_count": failure_count,
            f"{operation}.success_rate": success_rate,
            f"{operation}.duration": duration
        }
        
        for metric_name, value in metrics.items():
            record_metric(metric_name, value, tags)
            
    except Exception as e:
        logger.error(f"Failed to record batch metrics: {str(e)}", extra={
            "operation": operation,
            "success_count": success_count,
            "failure_count": failure_count,
            "duration": duration
        })

def track_resource_metrics(resource_type: str, metrics: Dict[str, float]) -> None:
    """Track resource utilization metrics.
    
    Args:
        resource_type: Type of resource (e.g., "cpu", "memory", "disk")
        metrics: Dictionary of metric names and values
    """
    try:
        base_tags = {"resource_type": resource_type}
        
        for metric_name, value in metrics.items():
            record_metric(f"resource.{resource_type}.{metric_name}", value, base_tags)
            
    except Exception as e:
        logger.error(f"Failed to record resource metrics: {str(e)}", extra={
            "resource_type": resource_type,
            "metrics": json.dumps(metrics)
        })