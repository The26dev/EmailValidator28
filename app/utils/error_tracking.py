"""Error tracking utilities for the monitoring system."""

from typing import Dict, Any, Optional
from datetime import datetime
from .metrics import increment_counter, record_metric
from .logger import logger

def track_error(
    error_type: str,
    error_message: str,
    additional_context: Optional[Dict[str, Any]] = None,
    severity: str = "error"
) -> None:
    """Track error metrics and logs with detailed context.
    
    Args:
        error_type: Category/type of the error
        error_message: Descriptive error message
        additional_context: Optional dictionary with error details
        severity: Error severity level (default: "error")
    """
    try:
        # Build error context
        context = {
            "error_type": error_type,
            "message": error_message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if additional_context:
            context.update(additional_context)
            
        # Record error metrics
        tags = {
            "type": error_type,
            "severity": severity
        }
        
        increment_counter("errors.total", tags)
        increment_counter(f"errors.{error_type}", tags)
        
        # Log error with context
        log_method = logger.error if severity == "error" else logger.warning
        log_method(f"{error_type}: {error_message}", extra=context)
        
    except Exception as e:
        logger.error(
            f"Failed to track error metric: {str(e)}",
            extra={
                "original_error": {
                    "type": error_type,
                    "message": error_message,
                    "context": additional_context
                },
                "tracking_error": str(e)
            }
        )