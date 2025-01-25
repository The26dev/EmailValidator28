// Error types and constants

export const ErrorTypes = {
    VALIDATION: 'validation',
    API: 'api',
    NETWORK: 'network',
    SECURITY: 'security',
    DATABASE: 'database',
    UNKNOWN: 'unknown'
};

export const ErrorSeverity = {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
    CRITICAL: 'critical'
};

export const ErrorMessages = {
    VALIDATION: {
        REQUIRED_FIELD: 'This field is required',
        INVALID_EMAIL: 'Please enter a valid email address',
        INVALID_FORMAT: 'Invalid format',
        NETWORK_ERROR: 'Network error occurred. Please try again',
        SERVER_ERROR: 'Server error occurred. Please try again later',
        UNKNOWN_ERROR: 'An unknown error occurred'
    }
};

export const HTTP_STATUS_CODES = {
    OK: 200,
    CREATED: 201,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    INTERNAL_SERVER_ERROR: 500
};