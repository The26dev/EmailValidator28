// Analytics System Implementation
import { performanceSystem } from '../systems/performance-system-updated';
import { dataVisualizer } from './data-visualizer';
import { loggingSystem } from '../systems/logging-system-updated';
import { errorSystem } from '../systems/error-system-updated';

class AnalyticsSystem {
    constructor() {
        this.logger = loggingSystem.child({ component: 'AnalyticsSystem' });
        this.dashboards = new Map();
        this.metrics = new Map();
        this.initialized = false;
    }

    async initialize(config = {}) {
        try {
            this.config = {
                updateInterval: 5000,
                retentionPeriod: 24 * 60 * 60 * 1000, // 24 hours
                aggregationInterval: 60 * 1000, // 1 minute
                endpoint: '/api/analytics',
                enableRealTime: true,
                ...config
            };

            // Initialize required systems
            await this.initializeSystems();

            // Create default dashboards
            await this.createDefaultDashboards();

            this.initialized = true;
            this.logger.info('Analytics system initialized');
        } catch (error) {
            this.logger.error('Failed to initialize analytics system', { error });
            throw error;
        }
    }

    async initializeSystems() {
        // Initialize required systems if not already initialized
        if (!performanceSystem.initialized) {
            await performanceSystem.initialize();
        }
        if (!dataVisualizer.initialized) {
            await dataVisualizer.initialize();
        }
    }

    async createDefaultDashboards() {
        // Performance Dashboard
        const perfDashboard = await this.createDashboard('performance', {
            title: 'Performance Metrics',
            description: 'System performance monitoring',
            charts: [
                { type: 'performance', metric: 'response-time' },
                { type: 'performance', metric: 'throughput' },
                { type: 'error-rate' }
            ]
        });

        // Validation Dashboard
        const validationDashboard = await this.createDashboard('validation', {
            title: 'Email Validation Metrics',
            description: 'Email validation statistics and results',
            charts: [
                { type: 'validation-results' },
                { type: 'performance', metric: 'validation-duration' }
            ]
        });

        // System Health Dashboard
        const healthDashboard = await this.createDashboard('system-health', {
            title: 'System Health',
            description: 'Overall system health and resources',
            charts: [
                { type: 'performance', metric: 'memory-usage' },
                { type: 'performance', metric: 'cpu-usage' },
                { type: 'performance', metric: 'api-latency' }
            ]
        });
    }

    async createDashboard(id, config) {
        try {
            const dashboard = {
                id,
                config,
                charts: new Map(),
                metrics: new Map(),
                created: new Date().toISOString()
            };

            // Create charts
            for (const chartConfig of config.charts) {
                const chart = await this.createChart(chartConfig);
                dashboard.charts.set(chart.id, chart);
            }

            this.dashboards.set(id, dashboard);
            this.logger.info('Dashboard created', { id });
            return dashboard;
        } catch (error) {
            this.logger.error('Failed to create dashboard', { id, error });
            throw error;
        }
    }

    async createChart(config) {
        const { type, metric } = config;
        let chart;

        switch (type) {
            case 'performance':
                chart = dataVisualizer.createPerformanceChart(metric, config);
                break;
            case 'validation-results':
                chart = dataVisualizer.createValidationResultsChart(config);
                break;
            case 'error-rate':
                chart = dataVisualizer.createErrorRateChart(config);
                break;
            default:
                throw new Error(`Unknown chart type: ${type}`);
        }

        return chart;
    }

    registerMetric(name, collector, config = {}) {
        const metricConfig = {
            interval: this.config.aggregationInterval,
            retention: this.config.retentionPeriod,
            aggregate: (data) => data.reduce((a, b) => a + b, 0) / data.length,
            ...config
        };

        const metric = {
            name,
            collector,
            config: metricConfig,
            data: [],
            lastUpdated: null
        };

        this.metrics.set(name, metric);
        
        // Start collection if real-time is enabled
        if (this.config.enableRealTime) {
            this.startMetricCollection(name);
        }
    }

    startMetricCollection(metricName) {
        const metric = this.metrics.get(metricName);
        if (!metric) return;

        const intervalId = setInterval(async () => {
            try {
                const value = await metric.collector();
                this.recordMetric(metricName, value);
            } catch (error) {
                this.logger.error('Failed to collect metric', {
                    metric: metricName,
                    error: error.message
                });
            }
        }, metric.config.interval);

        metric.intervalId = intervalId;
    }

    stopMetricCollection(metricName) {
        const metric = this.metrics.get(metricName);
        if (metric && metric.intervalId) {
            clearInterval(metric.intervalId);
            delete metric.intervalId;
        }
    }

    recordMetric(name, value, timestamp = Date.now()) {
        const metric = this.metrics.get(name);
        if (!metric) return;

        metric.data.push({ value, timestamp });
        metric.lastUpdated = timestamp;

        // Prune old data
        const cutoff = timestamp - metric.config.retention;
        metric.data = metric.data.filter(point => point.timestamp > cutoff);

        // Notify any subscribers
        this.notifyMetricUpdate(name, value, timestamp);
    }

    notifyMetricUpdate(name, value, timestamp) {
        // Update relevant charts
        this.dashboards.forEach(dashboard => {
            dashboard.charts.forEach(chart => {
                if (chart.config.metric === name) {
                    dataVisualizer.updateChartData(chart.id, [{
                        timestamp: new Date(timestamp),
                        value
                    }]);
                }
            });
        });
    }

    async getDashboard(id) {
        return this.dashboards.get(id);
    }

    async getMetricData(name, start = Date.now() - 3600000, end = Date.now()) {
        const metric = this.metrics.get(name);
        if (!metric) return null;

        return metric.data
            .filter(point => point.timestamp >= start && point.timestamp <= end)
            .sort((a, b) => a.timestamp - b.timestamp);
    }

    async generateReport(options = {}) {
        const {
            startTime = Date.now() - 24 * 60 * 60 * 1000,
            endTime = Date.now(),
            metrics = Array.from(this.metrics.keys())
        } = options;

        const report = {
            timestamp: new Date().toISOString(),
            timeRange: {
                start: new Date(startTime).toISOString(),
                end: new Date(endTime).toISOString()
            },
            metrics: {}
        };

        for (const metricName of metrics) {
            const data = await this.getMetricData(metricName, startTime, endTime);
            if (data) {
                const metric = this.metrics.get(metricName);
                report.metrics[metricName] = {
                    count: data.length,
                    average: metric.config.aggregate(data.map(d => d.value)),
                    min: Math.min(...data.map(d => d.value)),
                    max: Math.max(...data.map(d => d.value)),
                    lastValue: data[data.length - 1]?.value
                };
            }
        }

        return report;
    }

    async exportData(format = 'json') {
        const data = {
            timestamp: new Date().toISOString(),
            metrics: Object.fromEntries(
                Array.from(this.metrics.entries()).map(([name, metric]) => [
                    name,
                    metric.data
                ])
            ),
            dashboards: Object.fromEntries(
                Array.from(this.dashboards.entries()).map(([id, dashboard]) => [
                    id,
                    {
                        config: dashboard.config,
                        created: dashboard.created
                    }
                ])
            )
        };

        switch (format.toLowerCase()) {
            case 'json':
                return JSON.stringify(data, null, 2);
            case 'csv':
                return this.convertToCSV(data);
            default:
                throw new Error(`Unsupported export format: ${format}`);
        }
    }

    convertToCSV(data) {
        // Implementation of data to CSV conversion
        // This is a basic implementation that could be enhanced based on needs
        let csv = 'Metric,Timestamp,Value\n';
        
        Object.entries(data.metrics).forEach(([metric, points]) => {
            points.forEach(point => {
                csv += `${metric},${new Date(point.timestamp).toISOString()},${point.value}\n`;
            });
        });
        
        return csv;
    }

    async cleanup() {
        // Stop all metric collections
        for (const [name, metric] of this.metrics.entries()) {
            this.stopMetricCollection(name);
        }

        // Clear all dashboards
        for (const [id, dashboard] of this.dashboards.entries()) {
            dashboard.charts.forEach((chart, chartId) => {
                dataVisualizer.removeChart(chartId);
            });
        }

        // Clear data
        this.dashboards.clear();
        this.metrics.clear();

        this.initialized = false;
        this.logger.info('Analytics system cleaned up');
    }
}

// Export as singleton
export const analyticsSystem = new AnalyticsSystem();