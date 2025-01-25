// Enhanced Performance Monitoring System
import { errorSystem } from './error-system-updated';
import { loggingSystem } from './logging-system-updated';

class PerformanceSystem {
    constructor() {
        this.logger = loggingSystem.child({ component: 'PerformanceSystem' });
        this.metrics = new Map();
        this.thresholds = new Map();
        this.monitors = new Map();
        this.initialized = false;
    }

    async initialize(config = {}) {
        try {
            this.config = {
                endpoint: '/api/metrics',
                flushInterval: 10000, // 10 seconds
                maxQueueSize: 1000,
                enableRealTime: true,
                ...config
            };

            // Initialize performance observers
            this.initializeObservers();

            // Start periodic metrics flush
            this.flushIntervalId = setInterval(() => {
                this.flushMetrics().catch(error => {
                    this.logger.error('Failed to flush metrics', { error });
                });
            }, this.config.flushInterval);

            this.initialized = true;
            this.logger.info('Performance system initialized');
        } catch (error) {
            this.logger.error('Failed to initialize performance system', { error });
            throw error;
        }
    }

    initializeObservers() {
        // Performance Timeline observer
        this.observers = {
            longtask: new PerformanceObserver(this.handleLongTasks.bind(this)),
            resource: new PerformanceObserver(this.handleResources.bind(this)),
            navigation: new PerformanceObserver(this.handleNavigation.bind(this)),
            paint: new PerformanceObserver(this.handlePaint.bind(this))
        };

        // Observe different performance entry types
        this.observers.longtask.observe({ entryTypes: ['longtask'] });
        this.observers.resource.observe({ entryTypes: ['resource'] });
        this.observers.navigation.observe({ entryTypes: ['navigation'] });
        this.observers.paint.observe({ entryTypes: ['paint'] });
    }

    handleLongTasks(entries) {
        entries.getEntries().forEach(entry => {
            this.recordMetric('longtask', {
                duration: entry.duration,
                startTime: entry.startTime,
                name: entry.name
            });
        });
    }

    handleResources(entries) {
        entries.getEntries().forEach(entry => {
            this.recordMetric('resource', {
                name: entry.name,
                duration: entry.duration,
                size: entry.transferSize,
                type: entry.initiatorType
            });
        });
    }

    handleNavigation(entries) {
        entries.getEntries().forEach(entry => {
            this.recordMetric('navigation', {
                type: entry.type,
                loadTime: entry.loadEventEnd - entry.loadEventStart,
                domReady: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart
            });
        });
    }

    handlePaint(entries) {
        entries.getEntries().forEach(entry => {
            this.recordMetric('paint', {
                type: entry.name,
                startTime: entry.startTime
            });
        });
    }

    recordMetric(name, value, tags = {}) {
        if (!this.initialized) {
            this.logger.warn('Performance system not initialized');
            return;
        }

        const metric = {
            name,
            value,
            tags,
            timestamp: Date.now()
        };

        const key = `${name}:${JSON.stringify(tags)}`;
        if (!this.metrics.has(key)) {
            this.metrics.set(key, []);
        }
        this.metrics.get(key).push(metric);

        // Check thresholds
        this.checkThresholds(name, value, tags);

        // Auto-flush if queue is full
        if (this.getTotalMetrics() >= this.config.maxQueueSize) {
            this.flushMetrics().catch(error => {
                this.logger.error('Failed to flush metrics', { error });
            });
        }
    }

    getTotalMetrics() {
        let total = 0;
        for (const metrics of this.metrics.values()) {
            total += metrics.length;
        }
        return total;
    }

    setThreshold(name, threshold, callback) {
        this.thresholds.set(name, { threshold, callback });
    }

    checkThresholds(name, value, tags) {
        const threshold = this.thresholds.get(name);
        if (threshold && value > threshold.threshold) {
            this.logger.warn('Threshold exceeded', { name, value, threshold: threshold.threshold });
            threshold.callback({ name, value, tags });
        }
    }

    startMonitor(name) {
        this.monitors.set(name, performance.now());
    }

    endMonitor(name, tags = {}) {
        const startTime = this.monitors.get(name);
        if (startTime) {
            const duration = performance.now() - startTime;
            this.recordMetric(name, duration, tags);
            this.monitors.delete(name);
            return duration;
        }
        return null;
    }

    async flushMetrics() {
        if (!this.metrics.size) {
            return;
        }

        // Prepare metrics for transmission
        const metricsData = Array.from(this.metrics.values())
            .flat()
            .map(metric => ({
                ...metric,
                metadata: {
                    userAgent: navigator.userAgent,
                    url: window.location.href
                }
            }));

        try {
            const response = await fetch(this.config.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    metrics: metricsData,
                    timestamp: Date.now()
                })
            });

            if (!response.ok) {
                throw new Error(`Failed to send metrics: ${response.statusText}`);
            }

            // Clear sent metrics
            this.metrics.clear();
        } catch (error) {
            this.logger.error('Failed to flush metrics', { error });
            throw error;
        }
    }

    getMetricsSummary() {
        const summary = {
            total: this.getTotalMetrics(),
            types: {},
            latest: {}
        };

        for (const [key, metrics] of this.metrics.entries()) {
            const [name] = key.split(':');
            summary.types[name] = (summary.types[name] || 0) + metrics.length;
            summary.latest[name] = metrics[metrics.length - 1]?.value;
        }

        return summary;
    }

    async cleanup() {
        // Stop observers
        for (const observer of Object.values(this.observers)) {
            observer.disconnect();
        }

        // Clear intervals
        clearInterval(this.flushIntervalId);

        // Final metrics flush
        await this.flushMetrics();

        // Clear state
        this.metrics.clear();
        this.monitors.clear();
        this.initialized = false;

        this.logger.info('Performance system cleaned up');
    }
}

// Singleton instance
export const performanceSystem = new PerformanceSystem();