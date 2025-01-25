# Performance Monitoring System Documentation

## Overview

The performance monitoring system provides comprehensive performance tracking and monitoring capabilities, including:

- Real-time performance metrics collection
- Resource timing monitoring
- Long task detection
- Custom performance measurements
- Threshold monitoring
- Batched metrics transmission

## Features

1. Performance Entry Types
   - Navigation timing
   - Resource timing
   - Long tasks
   - Paint timing
   - Custom measurements

2. Metric Management
   - Automatic batching
   - Configurable thresholds
   - Custom tags support
   - Metric summarization

3. Integration
   - Error system integration
   - Logging system integration
   - Monitoring service integration

## Usage

### Basic Setup

```javascript
import { performanceSystem } from '../systems/performance-system-updated';

// Initialize with default config
await performanceSystem.initialize();

// Initialize with custom config
await performanceSystem.initialize({
    endpoint: '/api/custom-metrics',
    flushInterval: 5000,
    maxQueueSize: 500,
    enableRealTime: true
});
```

### Recording Metrics

```javascript
// Record simple metric
performanceSystem.recordMetric('api_response_time', 150);

// Record metric with tags
performanceSystem.recordMetric('api_call', 200, {
    endpoint: '/api/validate',
    method: 'POST'
});

// Monitor operation duration
performanceSystem.startMonitor('validation_process');
// ... perform operation
const duration = performanceSystem.endMonitor('validation_process', {
    batchSize: 100
});
```

### Setting Thresholds

```javascript
// Set threshold with callback
performanceSystem.setThreshold('api_response_time', 1000, ({ name, value, tags }) => {
    console.warn(`High response time detected: ${value}ms`);
    // Take action (e.g., alert, scale)
});
```

### Getting Metrics Summary

```javascript
const summary = performanceSystem.getMetricsSummary();
console.log('Performance Summary:', summary);
// {
//     total: 150,
//     types: {
//         api_response_time: 50,
//         validation_duration: 100
//     },
//     latest: {
//         api_response_time: 123,
//         validation_duration: 456
//     }
// }
```

## Performance Observers

### Long Tasks

```javascript
// Automatically monitors tasks taking longer than 50ms
// Recorded metrics include:
{
    name: 'longtask',
    value: {
        duration: 123,
        startTime: 1234567890,
        name: 'self'  // or 'same-origin', 'cross-origin', etc.
    }
}
```

### Resource Timing

```javascript
// Monitors resource loading performance
// Recorded metrics include:
{
    name: 'resource',
    value: {
        name: 'https://api.example.com/data',
        duration: 123,
        size: 1234,
        type: 'fetch'  // or 'script', 'img', etc.
    }
}
```

### Navigation Timing

```javascript
// Monitors page load performance
// Recorded metrics include:
{
    name: 'navigation',
    value: {
        type: 'navigate',
        loadTime: 1234,
        domReady: 567
    }
}
```

### Paint Timing

```javascript
// Monitors key rendering events
// Recorded metrics include:
{
    name: 'paint',
    value: {
        type: 'first-contentful-paint',
        startTime: 123
    }
}
```

## Best Practices

1. **Metric Naming**
   - Use consistent naming conventions
   - Include relevant context
   - Keep names descriptive but concise

2. **Tagging**
   - Add relevant tags for filtering
   - Include environment information
   - Tag by component/module

3. **Thresholds**
   - Set appropriate threshold levels
   - Include actionable callbacks
   - Monitor threshold triggers

4. **Resource Usage**
   - Use batch processing
   - Clean up monitors when done
   - Monitor queue size

## Integration with Other Systems

### With Error System

```javascript
try {
    performanceSystem.startMonitor('operation');
    // ... perform operation
} catch (error) {
    errorSystem.handleError(error, {
        type: 'performance',
        metrics: performanceSystem.getMetricsSummary()
    });
} finally {
    performanceSystem.endMonitor('operation');
}
```

### With Logging System

```javascript
// The system automatically logs important events
performanceSystem.logger.info('Performance metrics collected', {
    summary: performanceSystem.getMetricsSummary()
});
```

## Maintenance

1. **Cleanup**
```javascript
// Proper cleanup on application shutdown
await performanceSystem.cleanup();
```

2. **Monitor Queue Size**
```javascript
const metrics = performanceSystem.getMetricsSummary();
if (metrics.total > 1000) {
    // Handle high metric volume
}
```

3. **Regular Flushing**
```javascript
// Manual flush if needed
await performanceSystem.flushMetrics();
```

## Troubleshooting

1. **High Memory Usage**
   - Check queue size
   - Verify flush interval
   - Monitor metric volume

2. **Missing Metrics**
   - Verify initialization
   - Check observer setup
   - Validate metric recording

3. **Performance Impact**
   - Monitor observer overhead
   - Adjust batch sizes
   - Optimize threshold checks