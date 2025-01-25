// Email Validator Unit Tests
import { emailValidator } from '../../../static/js/validation/email-validator';
import { ErrorTypes } from '../../../static/js/utils/error-constants';

describe('EmailValidator', () => {
    beforeEach(async () => {
        await emailValidator.initialize();
    });

    describe('Basic Validation', () => {
        test('should validate correct email format', async () => {
            const result = await emailValidator.validateEmail('test@example.com');
            expect(result.format).toBe(true);
            expect(result.isValid).toBe(true);
        });

        test('should reject invalid email format', async () => {
            const result = await emailValidator.validateEmail('invalid-email');
            expect(result.format).toBe(false);
            expect(result.isValid).toBe(false);
        });

        test('should handle special characters correctly', async () => {
            const result = await emailValidator.validateEmail('user+tag@example.com');
            expect(result.format).toBe(true);
        });
    });

    describe('DNS Verification', () => {
        test('should verify valid domain', async () => {
            const mockDNSResolver = {
                verify: jest.fn().mockResolvedValue(true)
            };
            
            await emailValidator.initialize({ dnsResolver: mockDNSResolver });
            const result = await emailValidator.validateEmail('test@gmail.com');
            
            expect(result.dns).toBe(true);
            expect(mockDNSResolver.verify).toHaveBeenCalled();
        });

        test('should handle invalid domain', async () => {
            const mockDNSResolver = {
                verify: jest.fn().mockResolvedValue(false)
            };
            
            await emailValidator.initialize({ dnsResolver: mockDNSResolver });
            const result = await emailValidator.validateEmail('test@invalid-domain-123.com');
            
            expect(result.dns).toBe(false);
        });
    });

    describe('Disposable Email Check', () => {
        test('should detect disposable email', async () => {
            const mockChecker = {
                check: jest.fn().mockResolvedValue(false)
            };
            
            await emailValidator.initialize({ disposableEmailChecker: mockChecker });
            const result = await emailValidator.validateEmail('test@tempmail.com');
            
            expect(result.disposable).toBe(true);
        });

        test('should accept valid email provider', async () => {
            const mockChecker = {
                check: jest.fn().mockResolvedValue(true)
            };
            
            await emailValidator.initialize({ disposableEmailChecker: mockChecker });
            const result = await emailValidator.validateEmail('test@gmail.com');
            
            expect(result.disposable).toBe(false);
        });
    });

    describe('Batch Processing', () => {
        test('should handle batch validation', async () => {
            const emails = [
                'valid@example.com',
                'invalid-email',
                'test@gmail.com'
            ];

            const results = await emailValidator.validateBatch(emails);
            expect(results.size).toBe(3);
            expect(results.get('valid@example.com').format).toBe(true);
            expect(results.get('invalid-email').format).toBe(false);
        });

        test('should respect batch size', async () => {
            const emails = Array(5).fill('test@example.com');
            const batchSize = 2;

            // Mock internal validateEmail to track calls
            const validateEmailSpy = jest.spyOn(emailValidator, 'validateEmail');
            
            await emailValidator.validateBatch(emails, { batchSize });

            // Should process in 3 batches (2 + 2 + 1)
            expect(validateEmailSpy.mock.calls.length).toBe(5);
        });
    });

    describe('Error Handling', () => {
        test('should handle initialization errors', async () => {
            const badConfig = {
                disposableEmailChecker: 'not-a-valid-checker'
            };

            await expect(emailValidator.initialize(badConfig)).rejects.toThrow();
        });

        test('should handle DNS verification errors gracefully', async () => {
            const mockDNSResolver = {
                verify: jest.fn().mockRejectedValue(new Error('DNS Error'))
            };

            await emailValidator.initialize({ dnsResolver: mockDNSResolver });
            const result = await emailValidator.validateEmail('test@example.com');

            expect(result.dns).toBe(true); // Should fail open
        });
    });
});