// Enhanced Error Handling System

import { ErrorTypes, ErrorSeverity, ErrorMessages, HTTP_STATUS_CODES } from '../utils/error-constants';

class ErrorSystem {
    constructor() {
        this.handlers = new Map();
        this.errorLog = [];
        this.maxLogSize = 100;
        this.errorMetrics = new Map();
    }

    initialize() {
        this.setupGlobalHandlers();
        this.initializeErrorMetrics();
        this.setupErrorBoundary();
    }

    setupGlobalHandlers() {
        window.onerror = (message, source, lineno, colno, error) => {
            this.handleError(error || new Error(message), {
                source,
                lineno,
                colno,
                type: 'global'
            });
            return true; // Prevent default error handling
        };

        window.onunhandledrejection = (event) => {
            this.handleError(event.reason, {
                type: 'promise',
                unhandled: true
            });
        };
    }

    setupErrorBoundary() {
        class ErrorBoundary extends React.Component {
            constructor(props) {
                super(props);
                this.state = { hasError: false };
            }

            static getDerivedStateFromError(error) {
                return { hasError: true };
            }

            componentDidCatch(error, errorInfo) {
                this.props.errorSystem.handleError(error, {
                    type: 'react',
                    info: errorInfo
                });
            }

            render() {
                if (this.state.hasError) {
                    return this.props.fallback || <div>Something went wrong.</div>;
                }
                return this.props.children;
            }
        }
        this.ErrorBoundary = ErrorBoundary;
    }

    registerHandler(errorType, handler) {
        if (typeof handler !== 'function') {
            throw new Error('Handler must be a function');
        }
        this.handlers.set(errorType, handler);
    }

    handleError(error, context = {}) {
        const errorDetails = this.createErrorDetails(error, context);
        
        // Log the error
        this.logError(errorDetails);
        
        // Update metrics
        this.updateErrorMetrics(errorDetails);
        
        // Find and execute appropriate handler
        const handler = this.handlers.get(errorDetails.type) || this.defaultHandler;
        handler(errorDetails);

        // Report to monitoring service if serious
        if (this.isSerious(errorDetails)) {
            this.reportToMonitoring(errorDetails);
        }
    }

    createErrorDetails(error, context) {
        return {
            message: error.message,
            stack: error.stack,
            type: context.type || 'unknown',
            timestamp: new Date().toISOString(),
            context: {
                ...context,
                url: window.location.href,
                userAgent: navigator.userAgent
            },
            severity: this.calculateSeverity(error, context)
        };
    }

    calculateSeverity(error, context) {
        // Determine error severity based on type and context
        if (error.name === 'SecurityError') return 'critical';
        if (context.type === 'api') return 'high';
        if (context.type === 'validation') return 'low';
        return 'medium';
    }

    logError(errorDetails) {
        this.errorLog.unshift(errorDetails);
        if (this.errorLog.length > this.maxLogSize) {
            this.errorLog.pop();
        }
        console.error('Error occurred:', errorDetails);
    }

    updateErrorMetrics(errorDetails) {
        const key = `${errorDetails.type}:${errorDetails.severity}`;
        const count = (this.errorMetrics.get(key) || 0) + 1;
        this.errorMetrics.set(key, count);
    }

    getErrorMetrics() {
        return Object.fromEntries(this.errorMetrics);
    }

    clearErrorMetrics() {
        this.errorMetrics.clear();
    }

    isSerious(errorDetails) {
        return ['critical', 'high'].includes(errorDetails.severity);
    }

    async reportToMonitoring(errorDetails) {
        try {
            await fetch('/api/monitoring/error', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(errorDetails)
            });
        } catch (error) {
            console.error('Failed to report error to monitoring:', error);
        }
    }

    getErrorLog() {
        return [...this.errorLog];
    }

    clearErrorLog() {
        this.errorLog = [];
    }

    defaultHandler(errorDetails) {
        console.error('Unhandled error:', errorDetails);
        // Display user-friendly error message
        if (typeof document !== 'undefined') {
            const errorContainer = document.getElementById('error-container') || 
                document.createElement('div');
            errorContainer.id = 'error-container';
            errorContainer.className = 'error-message';
            errorContainer.textContent = 'An unexpected error occurred. Please try again later.';
            document.body.appendChild(errorContainer);
        }
    }
}

// Export as singleton
export const errorSystem = new ErrorSystem();