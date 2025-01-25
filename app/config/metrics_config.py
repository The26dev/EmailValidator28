"""Configuration settings for metrics collection."""

from typing import Optional
from pydantic import BaseSettings

class MetricsConfig(BaseSettings):
    """Metrics configuration settings."""
    
    STATSD_HOST: str = "localhost"
    STATSD_PORT: int = 8125
    STATSD_PREFIX: Optional[str] = "email_validator"
    
    class Config:
        env_prefix = "METRICS_"
        case_sensitive = True