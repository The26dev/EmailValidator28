# Getting Started with Email Validator Service

## Introduction
This guide will help you get started with using the Email Validator Service. We'll cover basic setup, running your first validation, and exploring advanced features.

## Prerequisites
- Python 3.8+
- Redis 6+
- PostgreSQL 12+
- Docker (optional)

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/your-org/email-validator.git
cd email-validator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy example configuration
cp config/system.example.json config/system.json

# Set required environment variables
export EMAIL_VALIDATOR_API_KEY="your-api-key"
export EMAIL_VALIDATOR_DB_URL="postgresql://user:pass@localhost/db"
export EMAIL_VALIDATOR_REDIS_URL="redis://localhost:6379/0"
```

### 3. Run Your First Validation
```python
from email_validator import EmailValidator

# Initialize validator
validator = EmailValidator()

# Validate a single email
result = validator.validate("test@example.com")
print(result.is_valid)  # True/False
print(result.details)   # Validation details
```

## Using the API

### 1. Authentication
All API requests require an API key in the `X-API-Key` header:
```bash
curl -X POST "http://localhost:8000/validate" \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com"}'
```

### 2. Basic Email Validation
```python
import requests

response = requests.post(
    "http://localhost:8000/validate",
    headers={"X-API-Key": "your-api-key"},
    json={"email": "test@example.com"}
)

result = response.json()
print(f"Is valid: {result['is_valid']}")
```

### 3. Batch Validation
```python
emails = ["test1@example.com", "test2@example.com"]
response = requests.post(
    "http://localhost:8000/validate/batch",
    headers={"X-API-Key": "your-api-key"},
    json={"emails": emails}
)

results = response.json()
print(f"Valid emails: {results['summary']['valid']}")
```

## Advanced Features

### 1. Validation Options
```python
# Enable additional checks
result = validator.validate(
    "test@example.com",
    options={
        "check_dns": True,
        "check_disposable": True,
        "check_typos": True,
        "check_reputation": True
    }
)
```

### 2. Custom Validation Rules
```python
# Add custom validation rule
validator.add_validation_rule(
    "custom_domain",
    lambda email: email.split("@")[1] in ["allowed.com", "trusted.org"]
)
```

### 3. Result Handling
```python
from email_validator import ResultsHandler

# Process validation results
handler = ResultsHandler()
collection = handler.create_collection(results)

# Get summary statistics
summary = collection.get_summary()
print(f"Total processed: {summary['total']}")
print(f"Valid emails: {summary['valid']}")

# Export results
csv_data = collection.export("csv")
```

## Error Handling

### 1. Common Errors
```python
try:
    result = validator.validate("invalid-email")
except ValidationError as e:
    print(f"Validation failed: {e.message}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
```

### 2. Error Responses
The API returns structured error responses:
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid email format"
    }
}
```

## Performance Optimization

### 1. Caching
Enable result caching to improve performance:
```python
validator = EmailValidator(
    cache_enabled=True,
    cache_ttl=3600  # 1 hour
)
```

### 2. Batch Processing
Process multiple emails efficiently:
```python
# Process in batches of 100
results = validator.validate_batch(
    emails,
    batch_size=100,
    parallel=True
)
```

## Monitoring and Logging

### 1. Enable Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email_validator")
```

### 2. Performance Metrics
```python
from email_validator.metrics import MetricsTracker

tracker = MetricsTracker()
tracker.track_validation(result)
print(f"Average response time: {tracker.get_average_response_time()}ms")
```

## Development Setup

### 1. Development Dependencies
```bash
pip install -r requirements-dev.txt
```

### 2. Running Tests
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
```

### 3. Code Style
```bash
# Format code
black app/ tests/

# Check types
mypy app/

# Lint code
flake8 app/ tests/
```

## Troubleshooting

### Common Issues

1. Connection Errors
```python
# Check database connection
from app.database import check_connection
is_connected = check_connection()

# Check Redis connection
from app.cache import check_cache
cache_available = check_cache()
```

2. API Key Issues
```python
# Validate API key
from app.auth import validate_key
is_valid = validate_key("your-api-key")
```

3. Rate Limiting
```python
# Check rate limit status
from app.rate_limiter import check_limit
limit_info = check_limit("your-api-key")
print(f"Remaining requests: {limit_info['remaining']}")
```

## Next Steps

1. Explore the [API Documentation](docs/api.md)
2. Review [Security Guidelines](docs/security_guidelines.md)
3. Check [Configuration Options](docs/configuration_management.md)
4. Set up [Monitoring](docs/deployment.md#monitoring-setup)

## Support
- GitHub Issues: [Report a bug](https://github.com/your-org/email-validator/issues)
- Documentation: [Full documentation](docs/)