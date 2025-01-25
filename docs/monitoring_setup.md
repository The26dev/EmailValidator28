# Monitoring System Setup Guide

## Overview
This guide describes how to set up and configure the monitoring system for the Email Validator Service.

## Prerequisites
- StatsD server
- Grafana (optional, for visualization)
- Access to environment configuration

## Configuration Steps

1. **Environment Variables**
   ```bash
   METRICS_STATSD_HOST=localhost
   METRICS_STATSD_PORT=8125
   METRICS_STATSD_PREFIX=email_validator
   ```

2. **StatsD Setup**
   - Install and configure StatsD
   - Ensure the service is running and accessible
   - Verify connectivity from the application

3. **Application Integration**
   - Import required monitoring utilities
   - Add performance tracking where needed
   - Implement error tracking in error handlers

4. **Validation**
   - Verify metrics are being recorded
   - Check error handling works as expected
   - Monitor system performance impact

## Key Metrics to Monitor

1. **System Health**
   - CPU usage
   - Memory utilization
   - Disk space
   - Service uptime

2. **Performance**
   - API response times
   - Validation durations
   - Cache hit rates
   - Database query times

3. **Errors**
   - Error rates by type
   - Status code distribution
   - Validation failure rates
   - System errors

4. **Business Metrics**
   - Validation requests per minute
   - Success/failure ratio
   - User activity
   - API usage by endpoint

## Maintenance

1. **Regular Tasks**
   - Monitor disk usage for metrics storage
   - Review and adjust sampling rates
   - Update alerting thresholds
   - Clean up old metrics data

2. **Troubleshooting**
   - Check application logs for metric errors
   - Verify StatsD connectivity
   - Monitor metric collection overhead
   - Review error handling effectiveness