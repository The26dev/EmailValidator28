# Logging System Documentation

## Overview

The logging system provides comprehensive logging capabilities for the Email Validator Service, including:

- Multiple log levels (DEBUG, INFO, WARN, ERROR, CRITICAL)
- Structured logging with context
- Batched log transmission
- Console output formatting
- Child loggers with inherited context
- Automatic queue management

## Usage

### Basic Logging

```javascript
import { loggingSystem } from '../systems/logging-system-updated';

// Initialize with default config
await loggingSystem.initialize();

// Log at different levels
loggingSystem.debug('Debug message');
loggingSystem.info('Info message', { user: 'test-user' });
loggingSystem.warn('Warning message', { operation: 'validation' });
loggingSystem.error('Error occurred', { error: err });
loggingSystem.critical('Critical system error', { component: 'database' });
```

### Configuration

```javascript
await loggingSystem.initialize({
    endpoint: '/api/logs',          // Log submission endpoint
    batchSize: 100,                 // Max logs per batch
    flushInterval: 5000,            // Flush interval in ms
    maxQueueSize: 1000,            // Max queued logs
    logLevel: 'INFO',              // Minimum log level
    enableConsole: true,           // Enable console output
    context: {                     // Global context
        app: 'email-validator',
        environment: 'production'
    }
});
```

### Child Loggers

```javascript
// Create a child logger with additional context
const moduleLogger = loggingSystem.child({
    module: 'email-validation',
    version: '1.0.0'
});

moduleLogger.info('Processing email', { email: 'test@example.com' });
// Includes both parent and child context
```

### Log Levels

Log levels in order of increasing severity:
1. DEBUG - Detailed information for debugging
2. INFO - General information about system operation
3. WARN - Warning messages for potential issues
4. ERROR - Error conditions that should be investigated
5. CRITICAL - Severe errors that require immediate attention

### Best Practices

1. **Use Appropriate Levels**
   - DEBUG for detailed troubleshooting
   - INFO for normal operation
   - WARN for potential issues
   - ERROR for actual errors
   - CRITICAL for severe issues

2. **Include Context**
   - Always add relevant context to logs
   - Include operation IDs for tracing
   - Add user/session information when available

3. **Structured Data**
   - Use objects for context instead of string concatenation
   - Include timestamps and correlation IDs
   - Add environment and component information

4. **Error Logging**
   - Include error objects in context
   - Add stack traces for debugging
   - Include relevant state information

## Integration

### With Error System

```javascript
import { errorSystem } from './error-system-updated';

try {
    // Operation
} catch (error) {
    loggingSystem.error('Operation failed', { error });
    errorSystem.handleError(error, { type: 'operation' });
}
```

### With Monitoring

The logging system automatically integrates with the monitoring system by:
- Sending batched logs to the monitoring endpoint
- Including metadata for analysis
- Supporting correlation with error tracking

## Performance Considerations

1. **Queue Management**
   - Logs are queued and sent in batches
   - Queue size is limited to prevent memory issues
   - Auto-flush occurs when queue is full

2. **Resource Usage**
   - Minimal impact on main thread
   - Efficient batching reduces network requests
   - Automatic cleanup of old logs

3. **Error Handling**
   - Failed transmissions are requeued
   - Circuit breaker prevents overwhelming servers
   - Graceful degradation if logging service is down

## Maintenance

1. **Cleanup**
   ```javascript
   // Proper cleanup on application shutdown
   await loggingSystem.cleanup();
   ```

2. **Log Level Adjustment**
   ```javascript
   // Adjust log level at runtime
   loggingSystem.setLogLevel('DEBUG');
   ```

3. **Queue Monitoring**
   ```javascript
   // Manual flush if needed
   await loggingSystem.flush();
   ```