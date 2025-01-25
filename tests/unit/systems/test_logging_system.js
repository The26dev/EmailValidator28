// Logging System Unit Tests
import { loggingSystem } from '../../../static/js/systems/logging-system-updated';

describe('LoggingSystem', () => {
    beforeEach(async () => {
        // Reset logging system before each test
        await loggingSystem.cleanup();
    });

    describe('Initialization', () => {
        test('should initialize with default config', async () => {
            await loggingSystem.initialize();
            expect(loggingSystem.initialized).toBe(true);
            expect(loggingSystem.getLogLevel()).toBe('INFO');
        });

        test('should initialize with custom config', async () => {
            await loggingSystem.initialize({
                logLevel: 'DEBUG',
                maxQueueSize: 500
            });
            expect(loggingSystem.getLogLevel()).toBe('DEBUG');
            expect(loggingSystem.maxQueueSize).toBe(500);
        });
    });

    describe('Log Levels', () => {
        beforeEach(async () => {
            await loggingSystem.initialize();
        });

        test('should respect log level hierarchy', () => {
            loggingSystem.setLogLevel('WARN');
            
            // Mock queue push
            const queuePush = jest.spyOn(loggingSystem.logQueue, 'push');
            
            loggingSystem.debug('Debug message');
            loggingSystem.info('Info message');
            loggingSystem.warn('Warning message');
            loggingSystem.error('Error message');
            
            // Only WARN and higher should be queued
            expect(queuePush).toHaveBeenCalledTimes(2);
        });

        test('should change log level', () => {
            loggingSystem.setLogLevel('ERROR');
            expect(loggingSystem.getLogLevel()).toBe('ERROR');
        });

        test('should throw on invalid log level', () => {
            expect(() => loggingSystem.setLogLevel('INVALID'))
                .toThrow('Invalid log level: INVALID');
        });
    });

    describe('Log Queue Management', () => {
        beforeEach(async () => {
            await loggingSystem.initialize({
                maxQueueSize: 3,
                flushInterval: 1000000 // Large interval to prevent auto-flush
            });
        });

        test('should auto-flush when queue is full', () => {
            const flush = jest.spyOn(loggingSystem, 'flush');
            
            loggingSystem.info('Message 1');
            loggingSystem.info('Message 2');
            loggingSystem.info('Message 3');
            loggingSystem.info('Message 4');
            
            expect(flush).toHaveBeenCalled();
        });

        test('should clear queue after successful flush', async () => {
            global.fetch = jest.fn().mockResolvedValue({
                ok: true
            });

            loggingSystem.info('Test message');
            await loggingSystem.flush();
            
            expect(loggingSystem.logQueue.length).toBe(0);
        });

        test('should requeue logs on failed flush', async () => {
            global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));

            loggingSystem.info('Test message');
            const originalQueue = [...loggingSystem.logQueue];
            await loggingSystem.flush();
            
            expect(loggingSystem.logQueue).toEqual(originalQueue);
        });
    });

    describe('Child Loggers', () => {
        beforeEach(async () => {
            await loggingSystem.initialize();
        });

        test('should create child logger with inherited context', async () => {
            const parentContext = { app: 'test-app' };
            await loggingSystem.initialize({ context: parentContext });
            
            const childLogger = loggingSystem.child({ module: 'test-module' });
            expect(childLogger.config.context).toEqual({
                app: 'test-app',
                module: 'test-module'
            });
        });

        test('should maintain separate log queues', () => {
            const childLogger = loggingSystem.child();
            
            loggingSystem.info('Parent message');
            childLogger.info('Child message');
            
            expect(loggingSystem.logQueue.length).toBe(1);
            expect(childLogger.logQueue.length).toBe(1);
        });
    });

    describe('Cleanup', () => {
        test('should flush remaining logs on cleanup', async () => {
            await loggingSystem.initialize();
            const flush = jest.spyOn(loggingSystem, 'flush');
            
            loggingSystem.info('Final message');
            await loggingSystem.cleanup();
            
            expect(flush).toHaveBeenCalled();
            expect(loggingSystem.initialized).toBe(false);
        });
    });
});