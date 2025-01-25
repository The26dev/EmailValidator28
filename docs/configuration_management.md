# Configuration Management Guide

## Overview
This document outlines the implementation details for the Email Validator Service configuration management system.

## Configuration Architecture

### 1. Configuration Loading System
```python
class ConfigurationLoader:
    def __init__(self):
        self.config = {}
        self.env_prefix = "EMAIL_VALIDATOR_"
        self.config_paths = [
            "/etc/email-validator/config.json",
            "~/.email-validator/config.json",
            "./config/system.json"
        ]

    def load_configuration(self):
        """
        Loads configuration in order of precedence:
        1. Environment variables
        2. Command line arguments
        3. Configuration files
        4. Default values
        """
        self.load_defaults()
        self.load_config_files()
        self.load_environment_vars()
        self.load_cli_args()
        self.validate_configuration()

    def get_config_value(self, key, default=None):
        """
        Gets configuration value with fallback handling
        """
        return self.config.get(key, default)
```

### 2. Dynamic Configuration
```python
class DynamicConfigManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.local_cache = {}
        self.watchers = []

    async def update_configuration(self, key, value):
        """
        Updates configuration in real-time
        """
        await self.redis.set(f"config:{key}", value)
        await self.notify_watchers(key, value)

    def register_watcher(self, callback):
        """
        Registers callback for config changes
        """
        self.watchers.append(callback)
```

### 3. Configuration Caching
```python
class ConfigurationCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 300  # 5 minutes

    async def get_cached_config(self, key):
        """
        Retrieves cached configuration
        """
        return await self.redis.get(f"config_cache:{key}")

    async def cache_config(self, key, value):
        """
        Caches configuration with TTL
        """
        await self.redis.set(
            f"config_cache:{key}",
            value,
            ex=self.ttl
        )
```

### 4. Override Mechanisms
```python
class ConfigurationOverride:
    def __init__(self):
        self.overrides = {}
        self.override_source = {}

    def set_override(self, key, value, source):
        """
        Sets configuration override with source tracking
        """
        self.overrides[key] = value
        self.override_source[key] = source

    def get_effective_value(self, key, base_value):
        """
        Gets effective value considering overrides
        """
        return self.overrides.get(key, base_value)
```

### 5. Fallback Handling
```python
class ConfigurationFallback:
    def __init__(self):
        self.fallback_chains = {}

    def define_fallback_chain(self, key, fallbacks):
        """
        Defines fallback chain for configuration key
        """
        self.fallback_chains[key] = fallbacks

    def get_with_fallback(self, key, configs):
        """
        Gets value using defined fallback chain
        """
        if key not in self.fallback_chains:
            return configs.get(key)

        for fallback_key in self.fallback_chains[key]:
            if fallback_key in configs:
                return configs[fallback_key]
```

## Implementation Examples

### 1. Basic Usage
```python
# Initialize configuration system
config_loader = ConfigurationLoader()
config = config_loader.load_configuration()

# Get configuration value with fallback
db_url = config.get_config_value(
    "database.url",
    "postgresql://localhost:5432/email_validator"
)
```

### 2. Dynamic Configuration Updates
```python
# Update configuration at runtime
async def update_rate_limit(new_limit):
    await dynamic_config.update_configuration(
        "rate_limiting.max_requests",
        new_limit
    )

# Register configuration change handler
def handle_config_change(key, value):
    if key == "rate_limiting.max_requests":
        update_rate_limiter(value)

dynamic_config.register_watcher(handle_config_change)
```

### 3. Cached Configuration Access
```python
# Get cached configuration
async def get_api_config():
    cached = await config_cache.get_cached_config("api")
    if cached:
        return cached

    config = load_api_config()
    await config_cache.cache_config("api", config)
    return config
```

## Configuration Schema

### 1. Base Configuration
```json
{
    "api": {
        "host": "0.0.0.0",
        "port": 8000,
        "workers": 4
    },
    "security": {
        "api_key_rotation_days": 90,
        "jwt_secret_key": "${JWT_SECRET}",
        "allowed_origins": ["https://example.com"]
    },
    "validation": {
        "batch_size": 100,
        "timeout_seconds": 30
    }
}
```

### 2. Environment Variables
```bash
# Core Settings
EMAIL_VALIDATOR_API_PORT=8000
EMAIL_VALIDATOR_LOG_LEVEL=INFO

# Security Settings
EMAIL_VALIDATOR_JWT_SECRET=your-secret-key
EMAIL_VALIDATOR_API_KEY_ROTATION_DAYS=90

# Database Settings
EMAIL_VALIDATOR_DB_URL=postgresql://user:pass@localhost/db

# Cache Settings
EMAIL_VALIDATOR_REDIS_URL=redis://localhost:6379/0
```

## Configuration Security

### 1. Sensitive Data Handling
- Use environment variables for secrets
- Encrypt sensitive configuration data
- Implement access controls for configuration changes

### 2. Validation Rules
```python
def validate_configuration(config):
    """
    Validates configuration against schema
    """
    schema = {
        "api": {
            "port": lambda x: 1024 <= x <= 65535,
            "workers": lambda x: x > 0
        },
        "security": {
            "api_key_rotation_days": lambda x: x > 0,
            "jwt_secret_key": lambda x: len(x) >= 32
        }
    }
    validate_against_schema(config, schema)
```

## Monitoring and Management

### 1. Configuration Auditing
```python
class ConfigurationAuditor:
    def __init__(self):
        self.audit_log = []

    def log_config_change(self, key, old_value, new_value, user):
        """
        Logs configuration changes for audit
        """
        self.audit_log.append({
            "timestamp": datetime.now(),
            "key": key,
            "old_value": old_value,
            "new_value": new_value,
            "user": user
        })
```

### 2. Health Checks
```python
async def check_configuration_health():
    """
    Checks configuration system health
    """
    return {
        "cache_available": await check_cache_connection(),
        "config_files_readable": check_config_files(),
        "required_values_present": validate_required_config()
    }
```

## Development Guidelines

### 1. Adding New Configuration
1. Define configuration key in schema
2. Add validation rules
3. Update documentation
4. Add migration plan if needed

### 2. Best Practices
- Use typed configuration values
- Document all configuration options
- Implement validation for all values
- Provide clear default values
- Include configuration in monitoring