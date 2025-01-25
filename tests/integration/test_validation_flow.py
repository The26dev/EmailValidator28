"""Integration tests for complete email validation flow."""
import pytest
import time
from unittest.mock import patch

from app.utils.validation_orchestrator import validate_email, validate_emails_batch
from app.utils.smtp_verifier import verify_smtp
from app.utils.dns_resolver import validate_dns
from app.utils.metrics import ValidationTimer
from ..conftest import VALID_TEST_EMAILS, INVALID_TEST_EMAILS

@pytest.mark.asyncio
async def test_full_validation_flow():
    """Test complete validation flow for valid email."""
    email = VALID_TEST_EMAILS[0]
    
    # Validate DNS first
    dns_result = validate_dns(email)
    assert dns_result["valid"]
    assert dns_result["details"]["mx_records"]
    
    # Then SMTP
    smtp_result = verify_smtp(email)
    assert smtp_result["valid"]
    assert smtp_result["code"] == 250
    
    # Finally full validation
    result = validate_email(email)
    assert result["valid"]
    assert result["score"] >= 0
    assert result["score"] <= 100
    assert result["checks"]["dns"]["valid"]
    assert result["checks"]["smtp"]["valid"]
    assert "created_at" in result

@pytest.mark.asyncio
async def test_validation_flow_invalid_dns():
    """Test validation flow with invalid DNS."""
    email = "test@nonexistent-domain-12345.com"
    
    # DNS should fail
    dns_result = validate_dns(email)
    assert not dns_result["valid"]
    
    # Full validation should reflect DNS failure
    result = validate_email(email)
    assert not result["valid"]
    assert not result["checks"]["dns"]["valid"]
    assert "dns" in result["checks"]["dns"]["error"].lower()

@pytest.mark.asyncio
async def test_validation_flow_smtp_failure():
    """Test validation flow with SMTP failure."""
    email = VALID_TEST_EMAILS[0]
    
    # Mock SMTP failure
    with patch("app.utils.smtp_verifier._check_smtp_server") as mock_smtp:
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        result = validate_email(email)
        assert not result["valid"]
        assert not result["checks"]["smtp"]["valid"]
        assert "smtp" in result["checks"]["smtp"]["error"].lower()

@pytest.mark.asyncio
async def test_batch_validation_flow():
    """Test batch validation flow."""
    emails = VALID_TEST_EMAILS[:2]
    results = await validate_emails_batch(emails)
    
    assert len(results) == len(emails)
    for result in results:
        assert "valid" in result
        assert "score" in result
        assert "checks" in result
        assert all(check in result["checks"] for check in ["dns", "smtp"])

def test_validation_performance():
    """Test validation performance with timing."""
    email = VALID_TEST_EMAILS[0]
    
    with ValidationTimer() as timer:
        result = validate_email(email)
        
    assert result["valid"]
    # Validation should complete in reasonable time
    assert timer.duration < 10  # seconds

@pytest.mark.asyncio
async def test_concurrent_validations():
    """Test concurrent validation processing."""
    emails = VALID_TEST_EMAILS + INVALID_TEST_EMAILS
    
    start_time = time.time()
    results = await validate_emails_batch(emails, batch_size=4)
    duration = time.time() - start_time
    
    assert len(results) == len(emails)
    # Batch processing should be faster than sequential
    assert duration < len(emails) * 2  # Average 2 seconds per email

@pytest.mark.asyncio
async def test_validation_retries():
    """Test validation retry behavior."""
    email = VALID_TEST_EMAILS[0]
    
    # Mock SMTP failure then success
    smtp_responses = [
        Exception("Temporary failure"),
        {"valid": True, "code": 250}
    ]
    with patch("app.utils.smtp_verifier._check_smtp_server") as mock_smtp:
        mock_smtp.side_effect = smtp_responses
        
        result = validate_email(email)
        assert result["valid"]
        assert result["checks"]["smtp"]["valid"]
        
def test_validation_error_handling():
    """Test error handling in validation flow."""
    # Test with various error conditions
    error_cases = [
        ("", "Invalid email format"),
        ("not-an-email", "Invalid email format"),
        ("missing@", "Invalid domain"),
        ("test@.", "Invalid domain"),
        (None, "Invalid input")
    ]
    
    for email, expected_error in error_cases:
        result = validate_email(email)
        assert not result["valid"]
        assert result["error"]
        assert expected_error.lower() in result["error"].lower()