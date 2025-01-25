# Email Validator Service - Deployment Guide

## Prerequisites

- Docker and Docker Compose
- AWS CLI (for production deployments)
- Python 3.8+
- PostgreSQL 13+
- Redis 6+

## Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Update the `.env` file with your actual configuration values:
```bash
# Update database configuration
DATABASE_URI=postgresql://actual_user:actual_password@your-db-host:5432/your_db

# Update Redis configuration
REDIS_URI=redis://your-redis-host:6379/0

# Set secure JWT configuration
JWT_SECRET=your-actual-secure-secret-key
JWT_ALGORITHM=HS256

# Set API keys
DISPOSABLE_EMAIL_API_KEY=your-actual-api-key
DOMAIN_REPUTATION_API_KEY=your-actual-api-key
```

3. Ensure your `.env` file is properly secured:
```bash
chmod 600 .env
```

## Production Environment Variables

For production deployments, we recommend using your cloud provider's secrets management service:

### AWS Setup
Use AWS Secrets Manager or Parameter Store:
```bash
# Store secrets
aws ssm put-parameter --name "/prod/email-validator/DATABASE_URI" --value "your-value" --type SecureString
aws ssm put-parameter --name "/prod/email-validator/JWT_SECRET" --value "your-value" --type SecureString

# Retrieve secrets in your deployment script
export DATABASE_URI=$(aws ssm get-parameter --name "/prod/email-validator/DATABASE_URI" --with-decryption --query Parameter.Value --output text)
export JWT_SECRET=$(aws ssm get-parameter --name "/prod/email-validator/JWT_SECRET" --with-decryption --query Parameter.Value --output text)
```

## Database Setup

1. Create the database:
```bash
createdb email_validator
```

2. Run migrations:
```bash
flask db upgrade
```

## Redis Setup

1. Install Redis:
```bash
sudo apt-get update
sudo apt-get install redis-server
```

2. Configure Redis:
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## Container Deployment

1. Build the containers:
```bash
docker-compose build
```

2. Start the services:
```bash
docker-compose up -d
```

## SSL/TLS Configuration

1. Install certbot:
```bash
sudo apt-get install certbot
```

2. Obtain SSL certificate:
```bash
sudo certbot certonly --webroot -w /var/www/html -d yourdomain.com
```

## Monitoring Setup

1. Configure logging:
```json
{
    "version": 1,
    "disable_existing_loggers": false,
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/main.log",
            "maxBytes": 5242880,
            "backupCount": 5
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file"]
    }
}
```

## Maintenance

Regular maintenance tasks:
```bash
# Backup database
pg_dump email_validator > backup.sql

# Rotate logs
logrotate /etc/logrotate.d/email-validator

# Check system health
./health_check.sh
```