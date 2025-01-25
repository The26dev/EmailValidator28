# Performance Testing Guide

## Overview
This directory contains performance tests for the Email Validator Service, including:
- Standard performance tests with pytest
- Load tests with Locust
- Component-level performance tests
- Concurrent validation tests

## Running Performance Tests

### Standard Tests
```bash
# Run all performance tests
pytest tests/performance/test_performance.py -v

# Run specific test
pytest tests/performance/test_performance.py -k "test_single_validation_performance"
```

### Load Tests
```bash
# Start Locust with web interface
locust -f tests/performance/locustfile.py

# Run from command line
locust -f tests/performance/locustfile.py --headless -u 100 -r 10 --run-time 5m
```

## Performance SLAs
- Single validation: < 2 seconds
- Batch validation: < 5 seconds
- API response time: < 500ms
- Throughput: > 10 validations/second
- Cache hit ratio: > 95%

## Test Categories
1. Single Validation Tests
   - Response time
   - Success rate
   - Component timing

2. Batch Validation Tests
   - Throughput
   - Concurrent processing
   - Resource usage

3. API Performance Tests
   - Response times
   - Rate limiting
   - Error handling

4. Component Tests
   - DNS resolution
   - SMTP verification
   - Cache performance

## Troubleshooting
Common issues and solutions:
- High latency: Check DNS/SMTP timeouts
- Low throughput: Monitor resource usage
- Cache misses: Verify cache configuration