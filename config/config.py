import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def validate_required_env_vars():
    """Validate that all required environment variables are set."""
    required_vars = [
        'DATABASE_URI',
        'REDIS_URI',
        'JWT_SECRET',
        'JWT_ALGORITHM',
        'SECRET_KEY',
        'DISPOSABLE_EMAIL_API_KEY',
        'DOMAIN_REPUTATION_API_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

validate_required_env_vars()

class Config:
    """Base configuration class."""
    # Database
    DATABASE_URI = os.getenv('DATABASE_URI')
    
    # External APIs
    DISPOSABLE_EMAIL_API_KEY = os.getenv('DISPOSABLE_EMAIL_API_KEY')
    DOMAIN_REPUTATION_API_KEY = os.getenv('DOMAIN_REPUTATION_API_KEY')
    
    # Rate Limiting
    RATE_LIMIT_MAX_REQUESTS = 100
    RATE_LIMIT_WINDOW_SECONDS = 60
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/main.log')
    LOG_MAX_BYTES = 5242880  # 5MB
    LOG_BACKUP_COUNT = 5
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Redis/Celery
    REDIS_URL = os.getenv('REDIS_URI')
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    # Use a separate test database
    DATABASE_URI = "postgresql+psycopg2://test_user:test_pass@localhost:5432/test_db"

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}