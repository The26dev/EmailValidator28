"""Tests for catch-all email detection functionality."""
import pytest
from unittest.mock import patch
from app.utils.catch_all_detector import (
    check_catch_all,
    _generate_test_emails,
    _calculate_confidence,
    is_likely_catch_all
)

@pytest.mark.asyncio
async def test_catch_all_detection_positive():
    """Test detection of catch-all domain."""
    domain = "catch-all-domain.com"
    
    # Mock DNS validation
    dns_result = {
        "valid": True,
        "details": {
            "mx_records": [(10, "mail.catch-all-domain.com")]
        }
    }
    
    # Mock SMTP verification to always return valid
    smtp_result = {
        "valid": True,
        "code": 250,
        "message": "OK",
        "details": {}
    }
    
    with patch("app.utils.catch_all_detector.validate_dns", return_value=dns_result), \
         patch("app.utils.catch_all_detector.verify_smtp", return_value=smtp_result):
        result = check_catch_all(domain)
        
        assert result["is_catch_all"]
        assert result["confidence"] > 0.9
        assert result["method_used"] == "random_sampling"
        assert not result["error"]

@pytest.mark.asyncio
async def test_catch_all_detection_negative():
    """Test detection of non-catch-all domain."""
    domain = "normal-domain.com"
    
    # Mock DNS validation
    dns_result = {
        "valid": True,
        "details": {
            "mx_records": [(10, "mail.normal-domain.com")]
        }
    }
    
    # Mock SMTP verification to always return invalid
    smtp_result = {
        "valid": False,
        "code": 550,
        "message": "User unknown",
        "details": {}
    }
    
    with patch("app.utils.catch_all_detector.validate_dns", return_value=dns_result), \
         patch("app.utils.catch_all_detector.verify_smtp", return_value=smtp_result):
        result = check_catch_all(domain)
        
        assert not result["is_catch_all"]
        assert result["confidence"] > 0.9
        assert result["method_used"] == "random_sampling"
        assert not result["error"]

def test_test_email_generation():
    """Test random test email generation."""
    domain = "test.com"
    count = 5
    
    emails = _generate_test_emails(domain, count)
    
    assert len(emails) == count
    for email in emails:
        assert email.endswith(f"@{domain}")
        assert "nonexistent_" in email
        assert len(email.split("@")[0]) > 20

def test_confidence_calculation():
    """Test confidence calculation logic."""
    # All same responses - high confidence
    responses = [
        {"code": 250},
        {"code": 250},
        {"code": 250}
    ]
    assert _calculate_confidence(responses) == 1.0
    
    # Mixed responses - lower confidence
    responses = [
        {"code": 250},
        {"code": 550},
        {"code": 250}
    ]
    confidence = _calculate_confidence(responses)
    assert 0 < confidence < 1.0
    
    # Empty responses
    assert _calculate_confidence([]) == 0.0

def test_likely_catch_all_assessment():
    """Test higher level catch-all assessment."""
    # Clear catch-all with high confidence
    result = {
        "catch_all": {
            "is_catch_all": True,
            "confidence": 0.9
        }
    }
    assert is_likely_catch_all(result)
    
    # Multiple risk signals
    result = {
        "catch_all": {
            "is_catch_all": False,
            "confidence": 0.5
        },
        "risk_score": 85,
        "reputation": {
            "risk_level": "high",
            "details": {
                "mail_config": {
                    "has_spf": False,
                    "has_dmarc": False
                }
            }
        }
    }
    assert is_likely_catch_all(result)
    
    # No risk signals
    result = {
        "catch_all": {
            "is_catch_all": False,
            "confidence": 0.5
        },
        "risk_score": 20,
        "reputation": {
            "risk_level": "low",
            "details": {
                "mail_config": {
                    "has_spf": True,
                    "has_dmarc": True
                }
            }
        }
    }
    assert not is_likely_catch_all(result)