# Data Visualization System Documentation

## Overview

The data visualization system provides comprehensive charting and visualization capabilities for monitoring and analyzing:

- Performance metrics
- Validation results
- Error rates
- System health
- Custom metrics

## Features

1. **Chart Types**
   - Line charts
   - Bar charts
   - Area charts
   - Scatter plots
   - Custom visualizations

2. **Real-time Updates**
   - Automatic data updates
   - Configurable intervals
   - Smooth animations
   - Data windowing

3. **Customization**
   - Themable
   - Responsive layouts
   - Custom styles
   - Flexible configurations

## Usage

### Basic Setup

```javascript
import { dataVisualizer } from '../analytics/data-visualizer';

// Initialize with default config
await dataVisualizer.initialize();

// Initialize with custom config
await dataVisualizer.initialize({
    containerId: 'custom-container',
    theme: 'dark',
    autoUpdate: true,
    updateInterval: 2000,
    animations: true,
    maxDataPoints: 50
});
```

### Creating Charts

```javascript
// Create basic chart
const chart = dataVisualizer.createChart('my-chart', {
    type: 'line',
    width: 800,
    height: 400,
    title: 'My Chart',
    xAxis: { label: 'Time' },
    yAxis: { label: 'Value' }
});

// Create performance chart
const perfChart = dataVisualizer.createPerformanceChart('api-response-time', {
    width: 600,
    height: 300
});

// Create validation results chart
const resultsChart = dataVisualizer.createValidationResultsChart();

// Create error rate chart
const errorChart = dataVisualizer.createErrorRateChart();
```

### Updating Data

```javascript
// Manual update
dataVisualizer.updateChartData('my-chart', [
    { timestamp: new Date(), value: 100 }
]);

// Auto-update setup
dataVisualizer.startAutoUpdate('my-chart', async () => {
    const newData = await fetchNewData();
    return newData;
}, 5000);

// Stop auto-updates
dataVisualizer.stopAutoUpdate('my-chart');
```

### Subscribing to Updates

```javascript
// Subscribe to chart updates
dataVisualizer.subscribe('my-chart', (data) => {
    console.log('Chart updated:', data);
});

// Unsubscribe when done
dataVisualizer.unsubscribe('my-chart', callback);
```

## Best Practices

1. **Chart Creation**
   - Use appropriate chart types
   - Set meaningful titles and labels
   - Configure proper dimensions
   - Consider data density

2. **Data Updates**
   - Use appropriate update intervals
   - Implement data windowing
   - Handle missing data gracefully
   - Monitor performance impact

3. **Resource Management**
   - Clean up unused charts
   - Manage update intervals
   - Remove unused subscriptions
   - Monitor memory usage

4. **Error Handling**
   - Handle data fetch failures
   - Validate input data
   - Provide fallback views
   - Log visualization errors

## Integration

### With Performance System

```javascript
// Create performance dashboard
const dashboard = {
    responseTime: dataVisualizer.createPerformanceChart('response-time'),
    throughput: dataVisualizer.createPerformanceChart('requests-per-minute'),
    errorRate: dataVisualizer.createErrorRateChart()
};

// Subscribe to updates
Object.entries(dashboard).forEach(([metric, chart]) => {
    dataVisualizer.subscribe(chart.id, (data) => {
        console.log(`${metric} updated:`, data);
    });
});
```

### With Validation System

```javascript
// Create validation results visualization
const resultsChart = dataVisualizer.createValidationResultsChart();

// Update with new validation results
validationSystem.on('batchComplete', (results) => {
    const chartData = processValidationResults(results);
    dataVisualizer.updateChartData(resultsChart.id, chartData);
});
```

## Themes

### Available Themes

1. Light Theme:
```javascript
{
    background: '#ffffff',
    text: '#2c3e50',
    grid: '#ecf0f1',
    accent: '#3498db'
}
```

2. Dark Theme:
```javascript
{
    background: '#2c3e50',
    text: '#ecf0f1',
    grid: '#34495e',
    accent: '#3498db'
}
```

### Custom Themes

```javascript
// Apply custom theme
dataVisualizer.applyTheme('custom-theme');

// Define custom colors
container.style.setProperty('--chart-background', '#f0f0f0');
container.style.setProperty('--chart-text', '#333333');
container.style.setProperty('--chart-grid', '#dddddd');
container.style.setProperty('--chart-accent', '#ff6b6b');
```

## Performance Considerations

1. **Data Volume**
   - Limit number of data points
   - Implement data aggregation
   - Use appropriate update intervals
   - Consider data windowing

2. **Rendering**
   - Use appropriate animations
   - Optimize SVG elements
   - Manage DOM updates
   - Consider device capabilities

3. **Resource Usage**
   - Monitor memory usage
   - Clean up unused resources
   - Optimize update intervals
   - Handle background/inactive tabs

## Troubleshooting

1. **Chart Not Rendering**
   - Verify container exists
   - Check data format
   - Validate dimensions
   - Review console errors

2. **Performance Issues**
   - Reduce data points
   - Adjust update interval
   - Disable animations
   - Profile rendering

3. **Memory Leaks**
   - Clean up charts properly
   - Remove event listeners
   - Clear intervals
   - Monitor memory usage

## Maintenance

1. **Cleanup**
```javascript
// Remove single chart
dataVisualizer.removeChart('my-chart');

// Clean up everything
await dataVisualizer.cleanup();
```

2. **Updates**
```javascript
// Manual data flush
dataVisualizer.updateChartData('my-chart', []);

// Reset auto-update interval
dataVisualizer.stopAutoUpdate('my-chart');
dataVisualizer.startAutoUpdate('my-chart', callback, newInterval);
```

3. **State Management**
```javascript
// Get chart state
const chart = dataVisualizer.charts.get('my-chart');
console.log('Chart state:', chart.data);

// Clear all subscriptions
dataVisualizer.subscribers.clear();
```