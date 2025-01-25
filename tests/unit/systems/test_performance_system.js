// Performance System Unit Tests
import { performanceSystem } from '../../../static/js/systems/performance-system-updated';

describe('PerformanceSystem', () => {
    beforeEach(async () => {
        await performanceSystem.cleanup();
    });

    describe('Initialization', () => {
        test('should initialize with default config', async () => {
            await performanceSystem.initialize();
            expect(performanceSystem.initialized).toBe(true);
        });

        test('should initialize with custom config', async () => {
            await performanceSystem.initialize({
                flushInterval: 5000,
                maxQueueSize: 500
            });
            expect(performanceSystem.config.flushInterval).toBe(5000);
            expect(performanceSystem.config.maxQueueSize).toBe(500);
        });
    });

    describe('Metric Recording', () => {
        beforeEach(async () => {
            await performanceSystem.initialize();
        });

        test('should record metrics correctly', () => {
            performanceSystem.recordMetric('test_metric', 100, { tag: 'test' });
            const summary = performanceSystem.getMetricsSummary();
            
            expect(summary.total).toBe(1);
            expect(summary.types.test_metric).toBe(1);
            expect(summary.latest.test_metric).toBe(100);
        });

        test('should handle multiple metrics', () => {
            performanceSystem.recordMetric('metric1', 100);
            performanceSystem.recordMetric('metric1', 200);
            performanceSystem.recordMetric('metric2', 300);
            
            const summary = performanceSystem.getMetricsSummary();
            expect(summary.total).toBe(3);
            expect(summary.types.metric1).toBe(2);
            expect(summary.types.metric2).toBe(1);
        });

        test('should trigger auto-flush when queue is full', async () => {
            const flush = jest.spyOn(performanceSystem, 'flushMetrics');
            const maxMetrics = performanceSystem.config.maxQueueSize;
            
            for (let i = 0; i <= maxMetrics; i++) {
                performanceSystem.recordMetric('test', i);
            }
            
            expect(flush).toHaveBeenCalled();
        });
    });

    describe('Monitoring', () => {
        beforeEach(async () => {
            await performanceSystem.initialize();
        });

        test('should measure duration correctly', () => {
            performanceSystem.startMonitor('test_operation');
            
            // Simulate some time passing
            jest.advanceTimersByTime(100);
            
            const duration = performanceSystem.endMonitor('test_operation');
            expect(duration).toBeGreaterThan(0);
        });

        test('should handle missing start time', () => {
            const duration = performanceSystem.endMonitor('nonexistent');
            expect(duration).toBeNull();
        });
    });

    describe('Thresholds', () => {
        beforeEach(async () => {
            await performanceSystem.initialize();
        });

        test('should trigger threshold callback', () => {
            const callback = jest.fn();
            performanceSystem.setThreshold('response_time', 100, callback);
            
            performanceSystem.recordMetric('response_time', 150);
            expect(callback).toHaveBeenCalled();
        });

        test('should not trigger threshold callback for normal values', () => {
            const callback = jest.fn();
            performanceSystem.setThreshold('response_time', 100, callback);
            
            performanceSystem.recordMetric('response_time', 50);
            expect(callback).not.toHaveBeenCalled();
        });
    });

    describe('Metrics Flushing', () => {
        beforeEach(async () => {
            await performanceSystem.initialize();
        });

        test('should flush metrics successfully', async () => {
            global.fetch = jest.fn().mockResolvedValue({
                ok: true
            });

            performanceSystem.recordMetric('test', 100);
            await performanceSystem.flushMetrics();
            
            expect(performanceSystem.getTotalMetrics()).toBe(0);
        });

        test('should handle flush failures', async () => {
            global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));

            performanceSystem.recordMetric('test', 100);
            await expect(performanceSystem.flushMetrics()).rejects.toThrow('Network error');
        });
    });

    describe('Cleanup', () => {
        test('should clean up resources', async () => {
            await performanceSystem.initialize();
            performanceSystem.recordMetric('test', 100);
            
            await performanceSystem.cleanup();
            
            expect(performanceSystem.initialized).toBe(false);
            expect(performanceSystem.getTotalMetrics()).toBe(0);
        });
    });
});