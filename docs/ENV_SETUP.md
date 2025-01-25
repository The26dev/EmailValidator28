# Environment Variables Setup Guide

## Overview
This document provides guidance on setting up environment variables for the application.

## Setup Instructions

1. Copy the example file:
```bash
cp .env.example .env
```

2. Update the values in `.env` with your actual configuration:
- Generate secure keys for `SECRET_KEY` and `JWT_SECRET_KEY`
- Configure your AWS credentials
- Set up database and Redis connection strings
- Adjust timeouts and cache settings as needed

## Required Variables

### Security
- `SECRET_KEY`: Main application secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### JWT Authentication
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `JWT_ALGORITHM`: Algorithm for JWT signing (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Access token lifetime
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token lifetime

### AWS Configuration
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region
- `KMS_KEY_ID`: KMS key ID for encryption

### Performance Settings
- `DNS_TIMEOUT`: DNS lookup timeout in seconds
- `DNS_LIFETIME`: DNS lookup total lifetime
- `DNS_CACHE_TTL`: DNS cache time-to-live
- `RATE_LIMIT`: Maximum requests per window
- `RATE_LIMIT_WINDOW`: Rate limit time window in seconds

## Development vs Production
- Development can use default values from `.env.example`
- Production must use secure, randomly generated keys
- Production should have proper AWS credentials
- Production should use external Redis for session storage

## Security Notes
- Never commit `.env` file to version control
- Regularly rotate secret keys and credentials
- Use proper key management in production
- Ensure secure transmission of environment variables to production servers