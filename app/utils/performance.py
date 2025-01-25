"""Performance measurement utilities."""

import time
from typing import Optional, Dict, Callable, Any
from contextlib import contextmanager
from functools import wraps
from .metrics import record_metric
from .logger import logger

def measure_execution_time(func: Callable) -> Callable:
    """Decorator to measure function execution time.
    
    Args:
        func: Function to measure
    
    Returns:
        Wrapped function that records execution time
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            metric_name = f"function.duration.{func.__name__}"
            try:
                record_metric(metric_name, duration)
            except Exception as e:
                logger.error(f"Failed to record function timing: {str(e)}", extra={
                    "function": func.__name__,
                    "duration": duration
                })
    return wrapper

@contextmanager
def measure_block(name: str, tags: Optional[Dict[str, str]] = None):
    """Context manager to measure execution time of a code block.
    
    Args:
        name: Name for the timing metric
        tags: Optional metric tags
        
    Example:
        with measure_block("validation_step", tags={"step": "dns"}):
            perform_dns_validation()
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        try:
            record_metric(f"block.duration.{name}", duration, tags)
        except Exception as e:
            logger.error(f"Failed to record block timing: {str(e)}", extra={
                "block": name,
                "duration": duration,
                "tags": tags
            })