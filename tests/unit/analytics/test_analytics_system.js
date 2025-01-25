// Analytics System Unit Tests
import { analyticsSystem } from '../../../static/js/analytics/analytics-system';
import { performanceSystem } from '../../../static/js/systems/performance-system-updated';
import { dataVisualizer } from '../../../static/js/analytics/data-visualizer';

describe('AnalyticsSystem', () => {
    beforeEach(async () => {
        await analyticsSystem.cleanup();
    });

    describe('Initialization', () => {
        test('should initialize with default config', async () => {
            await analyticsSystem.initialize();
            expect(analyticsSystem.initialized).toBe(true);
        });

        test('should initialize with custom config', async () => {
            await analyticsSystem.initialize({
                updateInterval: 2000,
                retentionPeriod: 12 * 60 * 60 * 1000
            });
            expect(analyticsSystem.config.updateInterval).toBe(2000);
            expect(analyticsSystem.config.retentionPeriod).toBe(12 * 60 * 60 * 1000);
        });
    });

    describe('Dashboard Management', () => {
        beforeEach(async () => {
            await analyticsSystem.initialize();
        });

        test('should create dashboard', async () => {
            const dashboardId = 'test-dashboard';
            const dashboard = await analyticsSystem.createDashboard(dashboardId, {
                title: 'Test Dashboard',
                description: 'Test description',
                charts: [
                    { type: 'performance', metric: 'test-metric' }
                ]
            });

            expect(analyticsSystem.dashboards.has(dashboardId)).toBe(true);
            expect(dashboard.charts.size).toBe(1);
        });

        test('should retrieve dashboard', async () => {
            const dashboardId = 'test-dashboard';
            const created = await analyticsSystem.createDashboard(dashboardId, {
                title: 'Test Dashboard',
                charts: []
            });
            
            const retrieved = await analyticsSystem.getDashboard(dashboardId);
            expect(retrieved).toBe(created);
        });
    });

    describe('Metric Management', () => {
        beforeEach(async () => {
            await analyticsSystem.initialize();
        });

        test('should register and collect metrics', async () => {
            const collector = jest.fn().mockResolvedValue(100);
            
            analyticsSystem.registerMetric('test-metric', collector, {
                interval: 100
            });

            // Wait for collection
            await new Promise(resolve => setTimeout(resolve, 150));
            
            const data = await analyticsSystem.getMetricData('test-metric');
            expect(data.length).toBeGreaterThan(0);
            expect(data[0].value).toBe(100);
        });

        test('should respect retention period', async () => {
            const now = Date.now();
            const metric = {
                name: 'test-metric',
                collector: () => Promise.resolve(100),
                config: {
                    retention: 1000 // 1 second
                }
            };

            analyticsSystem.metrics.set(metric.name, {
                ...metric,
                data: [
                    { timestamp: now - 2000, value: 1 }, // Should be removed
                    { timestamp: now - 500, value: 2 }, // Should be kept
                    { timestamp: now, value: 3 } // Should be kept
                ]
            });

            analyticsSystem.recordMetric(metric.name, 4, now + 100);
            
            const data = await analyticsSystem.getMetricData(metric.name);
            expect(data.length).toBe(3); // Only recent data points
        });
    });

    describe('Report Generation', () => {
        beforeEach(async () => {
            await analyticsSystem.initialize();
        });

        test('should generate report', async () => {
            const metric = 'test-metric';
            const now = Date.now();
            
            analyticsSystem.metrics.set(metric, {
                name: metric,
                data: [
                    { timestamp: now - 1000, value: 100 },
                    { timestamp: now, value: 200 }
                ],
                config: {
                    aggregate: values => values.reduce((a, b) => a + b, 0) / values.length
                }
            });

            const report = await analyticsSystem.generateReport({
                metrics: [metric]
            });

            expect(report.metrics[metric]).toBeDefined();
            expect(report.metrics[metric].average).toBe(150);
        });
    });

    describe('Data Export', () => {
        beforeEach(async () => {
            await analyticsSystem.initialize();
        });

        test('should export data as JSON', async () => {
            const metric = 'test-metric';
            const data = [
                { timestamp: Date.now(), value: 100 }
            ];

            analyticsSystem.metrics.set(metric, {
                name: metric,
                data
            });

            const exported = await analyticsSystem.exportData('json');
            const parsed = JSON.parse(exported);
            
            expect(parsed.metrics[metric]).toEqual(data);
        });

        test('should export data as CSV', async () => {
            const metric = 'test-metric';
            const timestamp = new Date().toISOString();
            const value = 100;

            analyticsSystem.metrics.set(metric, {
                name: metric,
                data: [{ timestamp, value }]
            });

            const csv = await analyticsSystem.exportData('csv');
            expect(csv).toContain('Metric,Timestamp,Value');
            expect(csv).toContain(`${metric},${timestamp},${value}`);
        });
    });

    describe('Cleanup', () => {
        test('should clean up resources', async () => {
            await analyticsSystem.initialize();

            analyticsSystem.registerMetric('test-metric', () => {});
            await analyticsSystem.createDashboard('test-dashboard', {
                title: 'Test',
                charts: []
            });

            await analyticsSystem.cleanup();

            expect(analyticsSystem.initialized).toBe(false);
            expect(analyticsSystem.metrics.size).toBe(0);
            expect(analyticsSystem.dashboards.size).toBe(0);
        });
    });
});