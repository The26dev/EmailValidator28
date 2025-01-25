"""Metrics collection and monitoring module.

This module provides functionality for:
- Performance metrics tracking
- Error rate monitoring
- Cache statistics collection
- API usage tracking
"""

import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from contextlib import contextmanager
import statsd
from ..config.metrics_config import MetricsConfig
from .logger import logger

# Load configuration
metrics_config = MetricsConfig()

# Initialize statsd client with configuration
try:
    STATSD_CLIENT = statsd.StatsClient(
        host=metrics_config.STATSD_HOST,
        port=metrics_config.STATSD_PORT,
        prefix=metrics_config.STATSD_PREFIX
    )
except Exception as e:
    logger.error(f"Failed to initialize StatsD client: {str(e)}")
    STATSD_CLIENT = None

@dataclass
class MetricData:
    """Container for metric data."""
    name: str
    value: float
    tags: Dict[str, str]
    timestamp: float

def record_metric(name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
    """Record a metric value with tags and error handling.
    
    Args:
        name: Name of the metric
        value: Numeric value of the metric
        tags: Optional dictionary of metric tags
    """
    if STATSD_CLIENT is None:
        logger.warning(f"StatsD client not initialized, skipping metric: {name}")
        return
        
    if tags is None:
        tags = {}
    
    metric = MetricData(
        name=name,
        value=value,
        tags=tags,
        timestamp=time.time()
    )
    
    # Send to statsd
    STATSD_CLIENT.gauge(f"{name}", value)
    
    # Log metric
    logger.debug(f"Recorded metric: {metric}")

@contextmanager
def timing_metric(name: str, tags: Optional[Dict[str, str]] = None):
    """Context manager to time operations and record duration.
    
    Args:
        name: Name of the timing metric
        tags: Optional dictionary of metric tags
        
    Example:
        with timing_metric("validation.process", tags={"type": "email"}):
            result = validate_email(email)
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        record_metric(f"{name}_duration", duration, tags)

def increment_counter(name: str, tags: Optional[Dict[str, str]] = None) -> None:
    """Increment a counter metric.
    
    Args:
        name: Name of the counter
        tags: Optional dictionary of metric tags
    """
    STATSD_CLIENT.incr(name)
    logger.debug(f"Incremented counter: {name}")

def track_api_call(endpoint: str, method: str, status_code: int, duration: float):
    """Record API call metrics.
    
    Args:
        endpoint: API endpoint path
        method: HTTP method
        status_code: Response status code
        duration: Request duration in seconds
    """
    tags = {
        'endpoint': endpoint,
        'method': method,
        'status_code': str(status_code)
    }
    
    record_metric('api.request.duration', duration, tags)
    increment_counter('api.requests.total', tags)
    
    if 200 <= status_code < 300:
        increment_counter('api.requests.success', tags)
    else:
        increment_counter('api.requests.error', tags)

def track_cache_metrics(hits: int, misses: int, size: int):
    """Record cache performance metrics.
    
    Args:
        hits: Number of cache hits
        misses: Number of cache misses
        size: Current cache size
    """
    record_metric('cache.hits', hits)
    record_metric('cache.misses', misses)
    record_metric('cache.size', size)
    
    if hits + misses > 0:
        hit_rate = hits / (hits + misses)
        record_metric('cache.hit_rate', hit_rate)

def track_error(error_type: str, error_message: str):
    """Record error metrics.
    
    Args:
        error_type: Type/category of error
        error_message: Error message
    """
    tags = {
        'error_type': error_type
    }
    
    increment_counter('errors.total', tags)
    logger.error(f"Error recorded: {error_type} - {error_message}")