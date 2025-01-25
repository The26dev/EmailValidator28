// Enhanced Validation Results Handler
import { errorSystem } from '../systems/error-system-updated';
import { loggingSystem } from '../systems/logging-system-updated';
import { ErrorTypes, ErrorMessages } from '../utils/error-constants';

class ValidationResult {
    constructor(email) {
        this.email = email;
        this.timestamp = new Date().toISOString();
        this.valid = false;
        this.score = 0;
        this.checks = {
            format: null,
            dns: null,
            disposable: null,
            reputation: null
        };
        this.details = [];
        this.errors = [];
        this.warnings = [];
        this.metadata = {};
    }

    addError(code, message) {
        this.errors.push({ code, message });
        this.valid = false;
    }

    addWarning(code, message) {
        this.warnings.push({ code, message });
    }

    addDetail(detail) {
        this.details.push(detail);
    }

    setCheck(name, passed, score = 0, details = null) {
        this.checks[name] = {
            passed,
            score,
            timestamp: new Date().toISOString(),
            details
        };
        this.updateScore();
    }

    updateScore() {
        const weights = {
            format: 0.3,
            dns: 0.3,
            disposable: 0.2,
            reputation: 0.2
        };

        let totalScore = 0;
        let totalWeight = 0;

        for (const [check, weight] of Object.entries(weights)) {
            if (this.checks[check]?.score !== null) {
                totalScore += this.checks[check].score * weight;
                totalWeight += weight;
            }
        }

        this.score = totalWeight > 0 ? totalScore / totalWeight : 0;
        this.valid = this.score >= 0.7; // Configurable threshold
    }

    setMetadata(key, value) {
        this.metadata[key] = value;
    }

    toJSON() {
        return {
            email: this.email,
            timestamp: this.timestamp,
            valid: this.valid,
            score: this.score,
            checks: this.checks,
            details: this.details,
            errors: this.errors,
            warnings: this.warnings,
            metadata: this.metadata
        };
    }
}

class ValidationResultsHandler {
    constructor() {
        this.logger = loggingSystem.child({ component: 'ValidationResultsHandler' });
        this.results = new Map();
        this.batchResults = new Map();
    }

    createResult(email) {
        const result = new ValidationResult(email);
        this.results.set(email, result);
        return result;
    }

    getResult(email) {
        return this.results.get(email);
    }

    async saveResult(result) {
        try {
            this.logger.debug('Saving validation result', {
                email: result.email,
                valid: result.valid
            });

            // Store in memory
            this.results.set(result.email, result);

            // Persist to storage
            await this.persistResult(result);

            return true;
        } catch (error) {
            this.logger.error('Failed to save validation result', {
                email: result.email,
                error: error.message
            });
            
            errorSystem.handleError(error, {
                type: ErrorTypes.DATABASE,
                operation: 'save_result',
                email: result.email
            });
            
            return false;
        }
    }

    async persistResult(result) {
        try {
            const response = await fetch('/api/validation/results', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(result)
            });

            if (!response.ok) {
                throw new Error(`Failed to persist result: ${response.statusText}`);
            }

            return true;
        } catch (error) {
            this.logger.error('Failed to persist validation result', {
                email: result.email,
                error: error.message
            });
            throw error;
        }
    }

    async getBatchResults(batchId) {
        try {
            const results = this.batchResults.get(batchId);
            if (!results) {
                this.logger.warn('Batch results not found', { batchId });
                return null;
            }

            return {
                batchId,
                timestamp: new Date().toISOString(),
                total: results.length,
                valid: results.filter(r => r.valid).length,
                invalid: results.filter(r => !r.valid).length,
                results: results
            };
        } catch (error) {
            this.logger.error('Failed to get batch results', {
                batchId,
                error: error.message
            });
            throw error;
        }
    }

    startBatch(batchId) {
        this.batchResults.set(batchId, []);
        this.logger.info('Started new validation batch', { batchId });
    }

    addToBatch(batchId, result) {
        const batch = this.batchResults.get(batchId);
        if (!batch) {
            throw new Error(`Batch ${batchId} not found`);
        }
        batch.push(result);
    }

    async finalizeBatch(batchId) {
        try {
            const results = this.batchResults.get(batchId);
            if (!results) {
                throw new Error(`Batch ${batchId} not found`);
            }

            const summary = {
                batchId,
                timestamp: new Date().toISOString(),
                total: results.length,
                valid: results.filter(r => r.valid).length,
                invalid: results.filter(r => !r.valid).length
            };

            // Persist batch results
            await this.persistBatchResults(batchId, summary);

            this.logger.info('Finalized validation batch', summary);
            return summary;
        } catch (error) {
            this.logger.error('Failed to finalize batch', {
                batchId,
                error: error.message
            });
            throw error;
        }
    }

    async persistBatchResults(batchId, summary) {
        try {
            const response = await fetch('/api/validation/batches', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    batchId,
                    results: this.batchResults.get(batchId),
                    summary
                })
            });

            if (!response.ok) {
                throw new Error(`Failed to persist batch results: ${response.statusText}`);
            }

            return true;
        } catch (error) {
            this.logger.error('Failed to persist batch results', {
                batchId,
                error: error.message
            });
            throw error;
        }
    }

    clearBatch(batchId) {
        this.batchResults.delete(batchId);
        this.logger.debug('Cleared batch results', { batchId });
    }

    generateReport(results) {
        return {
            timestamp: new Date().toISOString(),
            total: results.length,
            valid: results.filter(r => r.valid).length,
            invalid: results.filter(r => !r.valid).length,
            averageScore: results.reduce((acc, r) => acc + r.score, 0) / results.length,
            errorTypes: this.categorizeErrors(results),
            warningTypes: this.categorizeWarnings(results)
        };
    }

    categorizeErrors(results) {
        const errorTypes = new Map();
        for (const result of results) {
            for (const error of result.errors) {
                const count = errorTypes.get(error.code) || 0;
                errorTypes.set(error.code, count + 1);
            }
        }
        return Object.fromEntries(errorTypes);
    }

    categorizeWarnings(results) {
        const warningTypes = new Map();
        for (const result of results) {
            for (const warning of result.warnings) {
                const count = warningTypes.get(warning.code) || 0;
                warningTypes.set(warning.code, count + 1);
            }
        }
        return Object.fromEntries(warningTypes);
    }
}

// Export as singleton
export const validationResultsHandler = new ValidationResultsHandler();