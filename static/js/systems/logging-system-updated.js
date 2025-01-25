// Enhanced Logging System Implementation
import { errorSystem } from './error-system-updated';

class LoggingSystem {
    constructor() {
        this.logQueue = [];
        this.maxQueueSize = 1000;
        this.flushInterval = 5000; // 5 seconds
        this.initialized = false;
        this.logLevels = {
            DEBUG: 0,
            INFO: 1,
            WARN: 2,
            ERROR: 3,
            CRITICAL: 4
        };
        this.currentLevel = this.logLevels.INFO;
    }

    async initialize(config = {}) {
        try {
            this.config = {
                endpoint: '/api/logs',
                batchSize: 100,
                flushInterval: 5000,
                maxQueueSize: 1000,
                logLevel: 'INFO',
                enableConsole: true,
                context: {},
                ...config
            };

            this.currentLevel = this.logLevels[this.config.logLevel] || this.logLevels.INFO;
            this.maxQueueSize = this.config.maxQueueSize;
            this.flushInterval = this.config.flushInterval;

            // Start periodic flush
            this.flushIntervalId = setInterval(() => {
                this.flush().catch(error => {
                    console.error('Failed to flush logs:', error);
                });
            }, this.flushInterval);

            this.initialized = true;
            this.info('Logging system initialized', { component: 'LoggingSystem' });
        } catch (error) {
            console.error('Failed to initialize logging system:', error);
            errorSystem.handleError(error, { 
                type: 'system',
                component: 'LoggingSystem'
            });
        }
    }

    /**
     * Log a message at the specified level
     * @param {string} level - Log level
     * @param {string} message - Log message
     * @param {Object} context - Additional context
     */
    _log(level, message, context = {}) {
        if (!this.initialized) {
            console.warn('Logging system not initialized');
            return;
        }

        if (this.logLevels[level] < this.currentLevel) {
            return;
        }

        const logEntry = {
            timestamp: new Date().toISOString(),
            level,
            message,
            context: {
                ...this.config.context,
                ...context
            }
        };

        // Add to queue
        this.logQueue.push(logEntry);

        // Console output if enabled
        if (this.config.enableConsole) {
            this._consoleLog(logEntry);
        }

        // Auto-flush if queue is full
        if (this.logQueue.length >= this.maxQueueSize) {
            this.flush().catch(error => {
                console.error('Failed to flush logs:', error);
            });
        }
    }

    /**
     * Format and output log to console
     * @param {Object} logEntry - Log entry to output
     */
    _consoleLog(logEntry) {
        const { level, message, context } = logEntry;
        const timestamp = new Date().toISOString();
        const contextStr = Object.keys(context).length ? JSON.stringify(context) : '';
        
        const styles = {
            DEBUG: 'color: gray',
            INFO: 'color: blue',
            WARN: 'color: orange',
            ERROR: 'color: red',
            CRITICAL: 'color: red; font-weight: bold'
        };

        console.log(
            `%c[${level}]%c ${timestamp} - ${message} ${contextStr}`,
            styles[level] || '',
            'color: inherit'
        );
    }

    /**
     * Flush queued logs to server
     */
    async flush() {
        if (!this.logQueue.length) {
            return;
        }

        const logs = [...this.logQueue];
        this.logQueue = [];

        try {
            const response = await fetch(this.config.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    logs,
                    metadata: {
                        userAgent: navigator.userAgent,
                        timestamp: new Date().toISOString()
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`Failed to send logs: ${response.statusText}`);
            }
        } catch (error) {
            // Re-queue failed logs
            this.logQueue.unshift(...logs);
            errorSystem.handleError(error, {
                type: 'system',
                operation: 'log_flush',
                count: logs.length
            });
        }
    }

    // Convenience methods for different log levels
    debug(message, context = {}) {
        this._log('DEBUG', message, context);
    }

    info(message, context = {}) {
        this._log('INFO', message, context);
    }

    warn(message, context = {}) {
        this._log('WARN', message, context);
    }

    error(message, context = {}) {
        this._log('ERROR', message, context);
    }

    critical(message, context = {}) {
        this._log('CRITICAL', message, context);
    }

    /**
     * Set the current log level
     * @param {string} level - Log level to set
     */
    setLogLevel(level) {
        if (!(level in this.logLevels)) {
            throw new Error(`Invalid log level: ${level}`);
        }
        this.currentLevel = this.logLevels[level];
    }

    /**
     * Get current log level
     */
    getLogLevel() {
        return Object.keys(this.logLevels).find(
            key => this.logLevels[key] === this.currentLevel
        );
    }

    /**
     * Create a child logger with additional context
     * @param {Object} context - Additional context for the child logger
     */
    child(context = {}) {
        const childLogger = new LoggingSystem();
        childLogger.initialize({
            ...this.config,
            context: {
                ...this.config.context,
                ...context
            }
        });
        return childLogger;
    }

    /**
     * Clean up resources
     */
    async cleanup() {
        clearInterval(this.flushIntervalId);
        await this.flush();
        this.initialized = false;
    }
}

// Export as singleton
export const loggingSystem = new LoggingSystem();