# Validation Results Documentation

## Overview

The validation results system provides a structured approach to handling email validation results, including:

- Individual result management
- Batch processing
- Result persistence
- Report generation
- Error handling

## Result Structure

### Individual Result

```javascript
{
    "email": "user@example.com",
    "timestamp": "2023-04-01T12:00:00.000Z",
    "valid": true,
    "score": 0.85,
    "checks": {
        "format": {
            "passed": true,
            "score": 1.0,
            "timestamp": "2023-04-01T12:00:00.000Z",
            "details": null
        },
        "dns": {
            "passed": true,
            "score": 0.8,
            "details": {
                "hasMX": true,
                "hasA": true
            }
        },
        // Additional checks...
    },
    "details": [
        "Valid email format",
        "MX records found"
    ],
    "errors": [],
    "warnings": [
        {
            "code": "W001",
            "message": "Domain has low reputation score"
        }
    ],
    "metadata": {
        "processingTime": 245,
        "validatorVersion": "1.0.0"
    }
}
```

### Batch Results

```javascript
{
    "batchId": "batch-123",
    "timestamp": "2023-04-01T12:00:00.000Z",
    "summary": {
        "total": 100,
        "valid": 85,
        "invalid": 15,
        "averageScore": 0.82
    },
    "results": [
        // Individual results...
    ],
    "errorTypes": {
        "E001": 5,
        "E002": 10
    },
    "warningTypes": {
        "W001": 15,
        "W002": 8
    }
}
```

## Usage

### Individual Validation

```javascript
import { validationResultsHandler } from './validation/results-handler-updated';

// Create new result
const result = validationResultsHandler.createResult('test@example.com');

// Update checks
result.setCheck('format', true, 1.0);
result.setCheck('dns', true, 0.8, { hasMX: true });

// Add details
result.addDetail('Valid email format');

// Add warnings
result.addWarning('W001', 'Domain has low reputation');

// Save result
await validationResultsHandler.saveResult(result);
```

### Batch Processing

```javascript
// Start new batch
const batchId = 'batch-123';
validationResultsHandler.startBatch(batchId);

// Add results to batch
for (const email of emails) {
    const result = validationResultsHandler.createResult(email);
    // Perform validation...
    validationResultsHandler.addToBatch(batchId, result);
}

// Finalize batch
const summary = await validationResultsHandler.finalizeBatch(batchId);

// Clear batch data when done
validationResultsHandler.clearBatch(batchId);
```

### Report Generation

```javascript
const results = await validationResultsHandler.getBatchResults(batchId);
const report = validationResultsHandler.generateReport(results);

console.log('Validation Report:', report);
```

## Best Practices

1. **Result Creation**
   - Always use `createResult()` to ensure consistent structure
   - Set all relevant checks before saving
   - Include meaningful details and context

2. **Batch Processing**
   - Use batch operations for multiple validations
   - Clean up batch data after processing
   - Monitor batch size and performance

3. **Error Handling**
   - Always check for errors when saving results
   - Use appropriate error codes and messages
   - Include context in error details

4. **Performance**
   - Use batch processing for multiple validations
   - Clean up old results periodically
   - Monitor system resources

## Integration

### With Logging System

```javascript
// The handler automatically logs important events
validationResultsHandler.logger.info('Processing validation batch', {
    batchId,
    size: emails.length
});
```

### With Error System

```javascript
try {
    await validationResultsHandler.saveResult(result);
} catch (error) {
    errorSystem.handleError(error, {
        type: 'validation',
        email: result.email
    });
}
```

## Error Codes

### Validation Errors
- E001: Invalid email format
- E002: DNS resolution failed
- E003: Disposable email detected
- E004: Domain blacklisted
- E005: Invalid local part

### Warning Codes
- W001: Domain has low reputation
- W002: Unusual email pattern
- W003: Recently created domain
- W004: Mixed character sets
- W005: Potential typo in domain

## Maintenance

1. **Data Cleanup**
```javascript
// Clear old results periodically
validationResultsHandler.results.clear();
```

2. **Performance Monitoring**
```javascript
// Monitor result processing times
result.setMetadata('processingTime', endTime - startTime);
```

3. **Batch Management**
```javascript
// Monitor batch sizes
const batchSize = validationResultsHandler.batchResults.get(batchId).length;
if (batchSize > 1000) {
    // Split batch or handle differently
}
```