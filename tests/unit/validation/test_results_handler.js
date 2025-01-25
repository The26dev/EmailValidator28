// Validation Results Handler Unit Tests
import { validationResultsHandler } from '../../../static/js/validation/results-handler-updated';

describe('ValidationResultsHandler', () => {
    beforeEach(() => {
        // Clear any existing results
        validationResultsHandler.results.clear();
        validationResultsHandler.batchResults.clear();
    });

    describe('Individual Results', () => {
        test('should create new validation result', () => {
            const result = validationResultsHandler.createResult('test@example.com');
            
            expect(result.email).toBe('test@example.com');
            expect(result.valid).toBe(false);
            expect(result.score).toBe(0);
            expect(result.errors).toEqual([]);
        });

        test('should retrieve existing result', () => {
            const email = 'test@example.com';
            const created = validationResultsHandler.createResult(email);
            const retrieved = validationResultsHandler.getResult(email);
            
            expect(retrieved).toBe(created);
        });

        test('should update result score correctly', () => {
            const result = validationResultsHandler.createResult('test@example.com');
            
            result.setCheck('format', true, 1.0);
            result.setCheck('dns', true, 0.8);
            result.setCheck('disposable', false, 0.4);
            
            expect(result.score).toBeGreaterThan(0);
            expect(result.score).toBeLessThanOrEqual(1);
        });
    });

    describe('Batch Processing', () => {
        const batchId = 'test-batch-001';
        
        beforeEach(() => {
            validationResultsHandler.startBatch(batchId);
        });

        test('should handle batch operations', async () => {
            const email1 = validationResultsHandler.createResult('test1@example.com');
            const email2 = validationResultsHandler.createResult('test2@example.com');
            
            email1.setCheck('format', true, 1.0);
            email2.setCheck('format', false, 0);
            
            validationResultsHandler.addToBatch(batchId, email1);
            validationResultsHandler.addToBatch(batchId, email2);
            
            const summary = await validationResultsHandler.finalizeBatch(batchId);
            
            expect(summary.total).toBe(2);
            expect(summary.valid).toBe(1);
            expect(summary.invalid).toBe(1);
        });

        test('should throw error for invalid batch ID', () => {
            const result = validationResultsHandler.createResult('test@example.com');
            
            expect(() => {
                validationResultsHandler.addToBatch('invalid-batch', result);
            }).toThrow('Batch invalid-batch not found');
        });

        test('should clear batch results', () => {
            const result = validationResultsHandler.createResult('test@example.com');
            validationResultsHandler.addToBatch(batchId, result);
            
            validationResultsHandler.clearBatch(batchId);
            expect(validationResultsHandler.batchResults.has(batchId)).toBe(false);
        });
    });

    describe('Report Generation', () => {
        test('should generate comprehensive report', () => {
            const result1 = validationResultsHandler.createResult('test1@example.com');
            const result2 = validationResultsHandler.createResult('test2@example.com');
            
            result1.setCheck('format', true, 1.0);
            result1.addWarning('W001', 'Unusual domain');
            
            result2.setCheck('format', false, 0);
            result2.addError('E001', 'Invalid format');
            
            const report = validationResultsHandler.generateReport([result1, result2]);
            
            expect(report.total).toBe(2);
            expect(report.valid).toBe(1);
            expect(report.invalid).toBe(1);
            expect(report.errorTypes).toHaveProperty('E001');
            expect(report.warningTypes).toHaveProperty('W001');
        });
    });

    describe('Error Handling', () => {
        test('should handle persistence failures gracefully', async () => {
            // Mock fetch to simulate failure
            global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
            
            const result = validationResultsHandler.createResult('test@example.com');
            
            await expect(validationResultsHandler.persistResult(result))
                .rejects.toThrow('Network error');
        });
    });
});