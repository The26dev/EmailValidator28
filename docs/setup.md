# Email Validator Service - Setup Guide

## Prerequisites
- Python 3.8+
- Redis 6+
- PostgreSQL 12+
- Docker (optional)

## Local Development Setup

1. Create Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `API_KEY_SALT`: Salt for API key generation
- `PROMETHEUS_MULTIPROC_DIR`: Directory for Prometheus metrics

4. Initialize database:
```bash
python -m app.database_setup
```

5. Run development server:
```bash
uvicorn app.core_application:app --reload
```

## Docker Setup

1. Build image:
```bash
docker build -t email-validator .
```

2. Run with Docker Compose:
```bash
docker-compose up
```

This will start:
- API service
- Redis cache
- PostgreSQL database
- Prometheus monitoring
- Grafana dashboards

## Testing

1. Run unit tests:
```bash
pytest tests/test_utils/
```

2. Run integration tests:
```bash
pytest tests/integration/
```

3. Run performance tests:
```bash
pytest tests/performance/
```

4. Run load tests:
```bash
locust -f tests/performance/locustfile.py
```

## Development Tools

1. Code formatting:
```bash
black app/ tests/
```

2. Type checking:
```bash
mypy app/

3. Linting:
```bash
flake8 app/ tests/
```

4. Test coverage:
```bash
pytest --cov=app tests/
```

## Monitoring Setup

1. Prometheus metrics are available at `/metrics`

2. Import Grafana dashboards from:
```
app/monitoring/grafana/dashboards/
```

## Common Issues

1. DNS Resolution Issues
- Ensure correct DNS server configuration
- Check firewall rules for DNS ports

2. SMTP Verification Issues
- Configure SMTP timeouts appropriately
- Whitelist service IPs with email providers

3. Rate Limiting Issues
- Adjust Redis connection pool settings
- Monitor Redis memory usage

4. Performance Issues
- Tune worker processes/threads
- Optimize database queries
- Adjust cache TTLs