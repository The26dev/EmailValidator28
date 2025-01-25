// Data Visualizer Unit Tests
import { dataVisualizer } from '../../../static/js/analytics/data-visualizer';

describe('DataVisualizer', () => {
    beforeEach(async () => {
        // Reset data visualizer
        await dataVisualizer.cleanup();
        
        // Set up DOM environment
        document.body.innerHTML = '<div id="visualization-container"></div>';
    });

    describe('Initialization', () => {
        test('should initialize with default config', async () => {
            await dataVisualizer.initialize();
            expect(dataVisualizer.initialized).toBe(true);
        });

        test('should initialize with custom config', async () => {
            await dataVisualizer.initialize({
                theme: 'dark',
                updateInterval: 2000
            });
            expect(dataVisualizer.config.theme).toBe('dark');
            expect(dataVisualizer.config.updateInterval).toBe(2000);
        });

        test('should throw error for invalid container', async () => {
            document.body.innerHTML = '';
            await expect(dataVisualizer.initialize())
                .rejects.toThrow('Container with ID "visualization-container" not found');
        });
    });

    describe('Chart Management', () => {
        beforeEach(async () => {
            await dataVisualizer.initialize();
        });

        test('should create new chart', () => {
            const chart = dataVisualizer.createChart('test-chart');
            expect(dataVisualizer.charts.has('test-chart')).toBe(true);
            expect(chart.svg).toBeDefined();
        });

        test('should update chart data', () => {
            const chartId = 'test-chart';
            const chart = dataVisualizer.createChart(chartId);
            
            const newData = [
                { timestamp: new Date(), value: 100 }
            ];
            
            dataVisualizer.updateChartData(chartId, newData);
            expect(chart.data).toEqual(newData);
        });

        test('should remove chart', () => {
            const chartId = 'test-chart';
            dataVisualizer.createChart(chartId);
            dataVisualizer.removeChart(chartId);
            
            expect(dataVisualizer.charts.has(chartId)).toBe(false);
        });
    });

    describe('Auto Updates', () => {
        beforeEach(async () => {
            await dataVisualizer.initialize();
        });

        test('should start and stop auto updates', () => {
            const chartId = 'test-chart';
            dataVisualizer.createChart(chartId);
            
            const callback = jest.fn().mockResolvedValue([
                { timestamp: new Date(), value: 100 }
            ]);
            
            dataVisualizer.startAutoUpdate(chartId, callback, 1000);
            expect(dataVisualizer.updateIntervals.has(chartId)).toBe(true);
            
            dataVisualizer.stopAutoUpdate(chartId);
            expect(dataVisualizer.updateIntervals.has(chartId)).toBe(false);
        });
    });

    describe('Subscriptions', () => {
        beforeEach(async () => {
            await dataVisualizer.initialize();
        });

        test('should handle subscriptions', () => {
            const chartId = 'test-chart';
            const callback = jest.fn();
            
            dataVisualizer.createChart(chartId);
            dataVisualizer.subscribe(chartId, callback);
            
            const newData = [{ timestamp: new Date(), value: 100 }];
            dataVisualizer.updateChartData(chartId, newData);
            
            expect(callback).toHaveBeenCalledWith(newData);
        });

        test('should unsubscribe correctly', () => {
            const chartId = 'test-chart';
            const callback = jest.fn();
            
            dataVisualizer.createChart(chartId);
            dataVisualizer.subscribe(chartId, callback);
            dataVisualizer.unsubscribe(chartId, callback);
            
            dataVisualizer.updateChartData(chartId, []);
            expect(callback).not.toHaveBeenCalled();
        });
    });

    describe('Utility Charts', () => {
        beforeEach(async () => {
            await dataVisualizer.initialize();
        });

        test('should create performance chart', () => {
            const chart = dataVisualizer.createPerformanceChart('response-time');
            expect(chart).toBeDefined();
            expect(dataVisualizer.charts.has('performance-response-time')).toBe(true);
        });

        test('should create validation results chart', () => {
            const chart = dataVisualizer.createValidationResultsChart();
            expect(chart).toBeDefined();
            expect(dataVisualizer.charts.has('validation-results')).toBe(true);
        });

        test('should create error rate chart', () => {
            const chart = dataVisualizer.createErrorRateChart();
            expect(chart).toBeDefined();
            expect(dataVisualizer.charts.has('error-rate')).toBe(true);
        });
    });

    describe('Cleanup', () => {
        test('should clean up resources', async () => {
            await dataVisualizer.initialize();
            
            dataVisualizer.createChart('chart1');
            dataVisualizer.createChart('chart2');
            dataVisualizer.startAutoUpdate('chart1', jest.fn());
            
            await dataVisualizer.cleanup();
            
            expect(dataVisualizer.initialized).toBe(false);
            expect(dataVisualizer.charts.size).toBe(0);
            expect(dataVisualizer.updateIntervals.size).toBe(0);
        });
    });
});