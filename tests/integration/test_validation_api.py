"""Integration tests for email validation API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.core_application import main
from app.utils.validation_orchestrator import validate_email
from ..conftest import (
    VALID_TEST_EMAILS,
    INVALID_TEST_EMAILS,
    ROLE_ACCOUNT_EMAILS
)

@pytest.fixture
def api_client():
    """Create API test client."""
    app = main()
    return TestClient(app)

def test_validate_single_email_success(api_client, api_key):
    """Test successful single email validation."""
    email = VALID_TEST_EMAILS[0]
    response = api_client.post(
        "/validate/email",
        headers={"X-API-Key": api_key},
        json={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["email"] == email
    assert "metadata" in data
    assert "created_at" in data["data"]
    assert isinstance(data["data"]["score"], float)
    assert data["data"]["score"] >= 0
    assert data["data"]["score"] <= 100

def test_validate_single_email_invalid_format(api_client, api_key):
    """Test validation with invalid email format."""
    email = INVALID_TEST_EMAILS[0]
    response = api_client.post(
        "/validate/email",
        headers={"X-API-Key": api_key},
        json={"email": email}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_validate_batch_emails_success(api_client, api_key):
    """Test successful batch email validation."""
    emails = VALID_TEST_EMAILS[:2]
    response = api_client.post(
        "/validate/batch",
        headers={"X-API-Key": api_key},
        json={"emails": emails}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["results"]) == len(emails)
    assert "batch_id" in data["data"]
    assert "summary" in data["data"]
    assert data["data"]["summary"]["total"] == len(emails)

def test_validate_batch_emails_too_many(api_client, api_key):
    """Test batch validation with too many emails."""
    emails = ["test@example.com"] * 101  # Over 100 limit
    response = api_client.post(
        "/validate/batch",
        headers={"X-API-Key": api_key},
        json={"emails": emails}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_retrieve_validation_result(api_client, api_key):
    """Test retrieving validation result by ID."""
    # First run validation
    email = VALID_TEST_EMAILS[0]
    validate_response = api_client.post(
        "/validate/email",
        headers={"X-API-Key": api_key},
        json={"email": email}
    )
    validation_id = validate_response.json()["data"]["id"]
    
    # Then get result
    response = api_client.get(
        f"/results/{validation_id}",
        headers={"X-API-Key": api_key}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["id"] == validation_id
    assert data["data"]["email"] == email

def test_retrieve_nonexistent_result(api_client, api_key):
    """Test retrieving non-existent validation result."""
    response = api_client.get(
        "/results/nonexistent-id",
        headers={"X-API-Key": api_key}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"

def test_unauthorized_access(api_client):
    """Test API access without valid API key."""
    email = VALID_TEST_EMAILS[0]
    response = api_client.post(
        "/validate/email",
        json={"email": email}
    )
    
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTHENTICATION_ERROR"

def test_rate_limit_exceeded(api_client, api_key):
    """Test rate limiting."""
    # Mock rate limit check to force limit exceeded
    with patch("app.utils.rate_limiter.check_rate_limit", return_value=(False, {})):
        response = api_client.post(
            "/validate/email",
            headers={"X-API-Key": api_key},
            json={"email": VALID_TEST_EMAILS[0]}
        )
        
        assert response.status_code == 429
        data = response.json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert "Retry-After" in response.headers