# Email Validator Service API Documentation

## Overview
The Email Validator Service provides a REST API for validating email addresses using multiple validation methods including:
- Syntax validation
- DNS verification
- SMTP verification
- Role account detection
- Disposable email detection
- Domain reputation checks
- Catch-all detection

## Authentication
All API endpoints require authentication using an API key provided in the `X-API-Key` header.

## Rate Limiting
Rate limits vary by tier:
- Free: 30 requests/minute
- Basic: 100 requests/minute
- Premium: 300 requests/minute
- Enterprise: 1000 requests/minute

## Endpoints

### Single Email Validation
`POST /validate/email`

Validates a single email address.

**Request:**
```json
{
  "email": "test@example.com",
  "options": {
    "check_dns": true,
    "check_smtp": true,
    "check_reputation": true
  }
}
```

**Response:**
```json
{
  "status": "success",
  "metadata": {
    "request_id": "uuid",
    "path": "/validate/email",
    "timestamp": "2023-...",
    "duration_ms": 523.45
  },
  "data": {
    "id": "validation-uuid",
    "email": "test@example.com",
    "valid": true,
    "score": 85.5,
    "risk_level": "low",
    "checks": {
      "syntax": {"valid": true},
      "dns": {"valid": true, "details": {...}},
      "smtp": {"valid": true, "code": 250},
      "role_account": {"is_role": false},
      "disposable": {"is_disposable": false},
      "reputation": {"risk_level": "low", "score": 85.5}
    },
    "created_at": "2023-..."
  }
}
```

### Batch Email Validation
`POST /validate/batch`

Validates multiple email addresses in batch.

**Request:**
```json
{
  "emails": [
    "test1@example.com",
    "test2@example.com"
  ],
  "options": {
    "check_dns": true,
    "check_smtp": true
  }
}
```

**Response:**
```json
{
  "status": "success",
  "metadata": {...},
  "data": {
    "batch_id": "batch-uuid",
    "results": [{...}, {...}],
    "summary": {
      "total": 2,
      "valid": 1,
      "invalid": 1
    },
    "created_at": "2023-..."
  }
}
```

### Get Validation Result
`GET /results/{validation_id}`

Retrieves a stored validation result.

**Response:**
```json
{
  "status": "success",
  "metadata": {...},
  "data": {
    "id": "validation-uuid",
    "email": "test@example.com",
    ...
  }
}
```

## Error Responses

All error responses follow the format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {...}
  }
}
```

Common error codes:
- `VALIDATION_ERROR`: Invalid request parameters
- `AUTHENTICATION_ERROR`: Invalid/missing API key
- `RATE_LIMIT_EXCEEDED`: Rate limit reached
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `SERVICE_ERROR`: Internal service error

## Status Codes
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 429: Too Many Requests
- 500: Internal Server Error