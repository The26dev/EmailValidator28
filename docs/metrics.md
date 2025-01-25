# Metrics and Monitoring Documentation

## Overview

This document describes the metrics collection and monitoring system implemented in the Email Validator Service.

## Configuration

Metrics configuration is managed through environment variables with the `METRICS_` prefix:

- `METRICS_STATSD_HOST`: StatsD server host (default: "localhost")
- `METRICS_STATSD_PORT`: StatsD server port (default: 8125)
- `METRICS_STATSD_PREFIX`: Prefix for all metrics (default: "email_validator")

## Key Metrics

### API Metrics
- `api.request.duration`: Request duration in seconds
- `api.requests.total`: Total request count
- `api.requests.success`: Successful request count
- `api.requests.error`: Failed request count

### Error Metrics
- `errors.<error_type>`: Error count by type
- Each error metric includes:
  - Error message
  - Status code (if applicable)
  - Request path
  - Request method
  - Additional context

### System Metrics
- Cache performance metrics
- Validation performance metrics
- Resource utilization

## Best Practices

1. Always include relevant tags with metrics for better filtering
2. Use appropriate metric types (gauge vs counter)
3. Include error context when tracking errors
4. Handle metric recording failures gracefully