"""Application settings and configuration."""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Security Settings
    ENVIRONMENT: str = "development"
    
    # AWS Settings
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    KMS_KEY_ID: str = ""  # AWS KMS key ID for encryption
    SECRET_KEY: str = "your-super-secret-key-for-csrf-and-other-security-features"
    ALLOWED_HOSTS: list = ["localhost", "127.0.0.1"]
    
    # JWT Settings
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Session Settings
    SESSION_EXPIRE_DAYS: int = 7
    COOKIE_SECURE: bool = True
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "strict"
    
    # DNS Settings
    DNS_TIMEOUT: float = 2.0  # seconds
    DNS_LIFETIME: float = 4.0  # seconds
    DNS_CACHE_TTL: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()