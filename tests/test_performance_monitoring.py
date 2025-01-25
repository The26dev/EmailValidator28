"""Tests for performance monitoring utilities."""
import pytest
from app.utils.monitoring_utils import (
    get_resource_usage,
    check_performance_thresholds,
    log_performance_metrics
)

def test_get_resource_usage():
    """Test resource usage metrics collection."""
    metrics = get_resource_usage()
    
    # Verify required metrics are present
    assert 'cpu_percent' in metrics
    assert 'memory_percent' in metrics
    assert 'timestamp' in metrics
    
    # Verify metrics are within valid ranges
    assert 0 <= metrics['cpu_percent'] <= 100
    assert 0 <= metrics['memory_percent'] <= 100
    assert metrics['timestamp'] > 0

def test_check_performance_thresholds():
    """Test performance threshold checking."""
    # Test with metrics within thresholds
    good_metrics = {
        'cpu_percent': 70.0,
        'memory_percent': 75.0
    }
    assert check_performance_thresholds(good_metrics) == True
    
    # Test with metrics above thresholds
    bad_metrics = {
        'cpu_percent': 90.0,
        'memory_percent': 95.0
    }
    assert check_performance_thresholds(bad_metrics) == False

def test_log_performance_metrics(caplog):
    """Test performance metrics logging."""
    test_metrics = {
        'cpu_percent': 50.0,
        'memory_percent': 60.0,
        'network_io': {
            'bytes_sent': 1000,
            'bytes_recv': 2000
        }
    }
    
    log_performance_metrics(test_metrics)
    
    # Verify log message contains all metrics
    assert 'CPU: 50.0%' in caplog.text
    assert 'Memory: 60.0%' in caplog.text
    assert 'bytes sent: 1000' in caplog.text
    assert 'bytes received: 2000' in caplog.text