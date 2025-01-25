# Error Tracking Guide

## Overview

The error tracking system provides centralized error monitoring and metrics collection, with
comprehensive context and proper error handling.

## Key Features

1. **Metric Recording**
   - Error counts by type and severity
   - Detailed context for debugging
   - Automatic timestamp tracking
   - Tag-based filtering support

2. **Error Categories**
   - HTTP Errors
   - Validation Errors
   - Service Errors
   - System Errors
   - Performance Issues

3. **Context Collection**
   - Error type and message
   - Timestamp and severity
   - Request path and method
   - Component-specific details
   - Stack traces when relevant

## Usage Examples

### HTTP Errors
```python
track_error(
    error_type="http_error",
    error_message="Invalid request parameters",
    additional_context={
        "status_code": 400,
        "path": "/api/validate",
        "method": "POST"
    }
)
```

### Validation Errors
```python
track_error(
    error_type="validation_error",
    error_message="Invalid email format",
    additional_context={
        "email": email,
        "validation_step": "syntax"
    }
)
```

### Service Errors
```python
track_error(
    error_type="service_error",
    error_message="External API unavailable",
    additional_context={
        "service": "smtp_verification",
        "response_code": 503
    },
    severity="critical"
)
```

## Metric Types

1. **Counter Metrics**
   - `errors.total`: Total error count
   - `errors.<type>`: Errors by category
   - `errors.<type>.<severity>`: Errors by type and severity

2. **Tags**
   - `type`: Error category
   - `severity`: Error severity level
   - `component`: System component
   - Additional context-specific tags

## Error Handling

The error tracking system includes robust error handling to ensure that tracking failures don't
affect the core application:

1. Graceful handling of metric recording failures
2. Detailed logging of tracking errors
3. Fallback mechanisms for critical errors
4. Context preservation during failures