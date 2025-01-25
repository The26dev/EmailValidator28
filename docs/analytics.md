# Analytics System Documentation

## Overview

The analytics system provides comprehensive data collection, visualization, and analysis capabilities for the Email Validator Service, including:

- Real-time metric collection
- Customizable dashboards
- Automated reporting
- Data export
- Integration with performance monitoring

## Features

1. **Metric Collection**
   - Real-time data collection
   - Configurable intervals
   - Data retention policies
   - Custom aggregations

2. **Dashboards**
   - Multiple visualization types
   - Real-time updates
   - Customizable layouts
   - Interactive charts

3. **Reporting**
   - Automated report generation
   - Custom time ranges
   - Multiple export formats
   - Aggregated statistics

## Usage

### Basic Setup

```javascript
import { analyticsSystem } from './analytics/analytics-system';

// Initialize with default config
await analyticsSystem.initialize();

// Initialize with custom config
await analyticsSystem.initialize({
    updateInterval: 5000,
    retentionPeriod: 24 * 60 * 60 * 1000, // 24 hours
    aggregationInterval: 60 * 1000, // 1 minute
    enableRealTime: true
});
```

### Creating Dashboards

```javascript
// Create custom dashboard
const dashboard = await analyticsSystem.createDashboard('custom-dashboard', {
    title: 'Custom Metrics',
    description: 'Custom performance metrics',
    charts: [
        {
            type: 'performance',
            metric: 'response-time',
            title: 'API Response Time'
        },
        {
            type: 'validation-results',
            title: 'Validation Results'
        }
    ]
});

// Get existing dashboard
const performanceDashboard = await analyticsSystem.getDashboard('performance');
```

### Metric Registration

```javascript
// Register custom metric
analyticsSystem.registerMetric('custom-metric', async () => {
    // Collect metric value
    return await getMetricValue();
}, {
    interval: 10000,
    retention: 7 * 24 * 60 * 60 * 1000, // 7 days
    aggregate: values => values.reduce((a, b) => a + b, 0) / values.length
});
```

### Report Generation

```javascript
// Generate custom report
const report = await analyticsSystem.generateReport({
    startTime: Date.now() - 24 * 60 * 60 * 1000, // Last 24 hours
    endTime: Date.now(),
    metrics: ['response-time', 'error-rate']
});

console.log('Analytics Report:', report);
```

### Data Export

```javascript
// Export as JSON
const jsonData = await analyticsSystem.exportData('json');

// Export as CSV
const csvData = await analyticsSystem.exportData('csv');
```

## Best Practices

1. **Metric Collection**
   - Choose appropriate collection intervals
   - Set reasonable retention periods
   - Use meaningful metric names
   - Include relevant context

2. **Dashboard Design**
   - Group related metrics
   - Use appropriate chart types
   - Set meaningful titles and labels
   - Consider data density

3. **Performance**
   - Monitor collection overhead
   - Aggregate high-frequency metrics
   - Clean up unused dashboards
   - Optimize data retention

4. **Resource Management**
   - Stop unused metric collections
   - Remove unnecessary dashboards
   - Clear old data regularly
   - Monitor memory usage

## Integration

### With Performance System

```javascript
// Register performance metrics
analyticsSystem.registerMetric('cpu-usage', async () => {
    const metrics = await performanceSystem.getMetricsSummary();
    return metrics.latest['cpu-usage'];
});

// Create performance dashboard
const dashboard = await analyticsSystem.createDashboard('system-metrics', {
    title: 'System Metrics',
    charts: [
        { type: 'performance', metric: 'cpu-usage' },
        { type: 'performance', metric: 'memory-usage' }
    ]
});
```

### With Validation System

```javascript
// Create validation dashboard
const dashboard = await analyticsSystem.createDashboard('validation-metrics', {
    title: 'Validation Metrics',
    charts: [
        { type: 'validation-results' },
        { type: 'performance', metric: 'validation-duration' }
    ]
});
```

## Maintenance

1. **Cleanup**
```javascript
// Proper cleanup on shutdown
await analyticsSystem.cleanup();
```

2. **Data Management**
```javascript
// Get metric data for specific period
const data = await analyticsSystem.getMetricData('metric-name', startTime, endTime);

// Export data for backup
const backup = await analyticsSystem.exportData('json');
```

3. **Dashboard Management**
```javascript
// Remove unused dashboard
analyticsSystem.dashboards.delete('old-dashboard');

// Update chart configuration
const dashboard = await analyticsSystem.getDashboard('dashboard-id');
dashboard.charts.forEach(chart => {
    chart.config.updateInterval = 10000;
});
```

## Troubleshooting

1. **Missing Data**
   - Check metric collection status
   - Verify collection intervals
   - Check retention settings
   - Review error logs

2. **Performance Issues**
   - Adjust collection intervals
   - Optimize retention periods
   - Review metric aggregation
   - Monitor resource usage

3. **Visualization Problems**
   - Verify chart configuration
   - Check data format
   - Validate dashboard setup
   - Review browser console