"""Pytest configuration and fixtures.

This module sets up common test fixtures and configuration used across tests.
"""
import os
import pytest
from typing import Dict, Generator
from fastapi.testclient import TestClient
from fakeredis import FakeRedis

from app.core_application import main
from app.utils.cache_manager import cache

# Test data
VALID_TEST_EMAILS = [
    "test@example.com",
    "user.name@company.co.uk",
    "admin@localhost"
]

INVALID_TEST_EMAILS = [
    "not-an-email",
    "@no-local-part.com",
    "no-at-sign.com",
    "spaces in@email.com",
    ".leading-dot@domain.com"
]

ROLE_ACCOUNT_EMAILS = [
    "admin@company.com",
    "support@service.net",
    "noreply@system.org"
]

DISPOSABLE_EMAILS = [
    "test@tempmail.com",
    "user@throwawaymail.com",
    "temp@10minutemail.com"
]

@pytest.fixture
def test_client() -> Generator:
    """Create a FastAPI test client."""
    app = main()
    with TestClient(app) as client:
        yield client

@pytest.fixture
def fake_redis() -> Generator:
    """Create a fake Redis instance for testing."""
    redis = FakeRedis()
    # Store original Redis client
    original = cache.redis
    # Replace with fake Redis
    cache.redis = redis
    yield redis
    # Restore original Redis client
    cache.redis = original

@pytest.fixture
def api_key() -> str:
    """Get test API key."""
    return "test-api-key"

@pytest.fixture
def auth_headers(api_key: str) -> Dict[str, str]:
    """Get headers with test API key."""
    return {"X-API-Key": api_key}