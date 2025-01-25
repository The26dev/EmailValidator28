"""Tests for SMTP verification functionality."""
import pytest
from unittest.mock import Mock, patch
from smtplib import SMTPException
from app.utils.smtp_verifier import verify_smtp, SMTPResult

@pytest.mark.asyncio
async def test_smtp_verification_success():
    """Test successful SMTP verification."""
    email = "test@example.com"
    domain = "example.com"
    mx_host = "mail.example.com"
    
    # Mock DNS validation result
    dns_result = {
        "valid": True,
        "details": {
            "mx_records": [(10, mx_host)]
        }
    }
    
    # Mock SMTP connection
    smtp_mock = Mock()
    smtp_mock.has_extn.return_value = True
    smtp_mock.mail.return_value = None
    smtp_mock.rcpt.return_value = (250, b"OK")
    
    with patch("app.utils.smtp_verifier.validate_dns", return_value=dns_result), \
         patch("smtplib.SMTP") as smtp_class:
        smtp_class.return_value.__enter__.return_value = smtp_mock
        
        result = verify_smtp(email)
        
        assert result["valid"]
        assert result["code"] == 250
        assert result["supports_tls"]
        assert not result["error"]

@pytest.mark.asyncio
async def test_smtp_verification_dns_failure():
    """Test SMTP verification with DNS validation failure."""
    email = "test@invalid.com"
    
    # Mock failed DNS validation
    dns_result = {
        "valid": False,
        "details": {
            "error": "DNS lookup failed"
        }
    }
    
    with patch("app.utils.smtp_verifier.validate_dns", return_value=dns_result):
        result = verify_smtp(email)
        
        assert not result["valid"]
        assert "DNS validation failed" in result["error"]

@pytest.mark.asyncio
async def test_smtp_verification_connection_failure():
    """Test SMTP verification with connection failure."""
    email = "test@example.com"
    domain = "example.com"
    mx_host = "mail.example.com"
    
    # Mock DNS validation result
    dns_result = {
        "valid": True,
        "details": {
            "mx_records": [(10, mx_host)]
        }
    }
    
    # Mock SMTP connection failure
    with patch("app.utils.smtp_verifier.validate_dns", return_value=dns_result), \
         patch("smtplib.SMTP") as smtp_class:
        smtp_class.return_value.__enter__.side_effect = SMTPException("Connection failed")
        
        result = verify_smtp(email)
        
        assert not result["valid"]
        assert "All MX servers failed verification" in result["error"]

@pytest.mark.asyncio
async def test_smtp_verification_no_mx_records():
    """Test SMTP verification with no MX records."""
    email = "test@example.com"
    
    # Mock DNS validation with no MX records
    dns_result = {
        "valid": True,
        "details": {
            "mx_records": []
        }
    }
    
    with patch("app.utils.smtp_verifier.validate_dns", return_value=dns_result):
        result = verify_smtp(email)
        
        assert not result["valid"]
        assert "No MX records found" in result["error"]