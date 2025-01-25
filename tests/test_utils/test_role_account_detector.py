"""Tests for role account detection functionality."""
import pytest
from app.utils.role_account_detector import check_role_account

def test_role_account_detection_basic():
    """Test basic role account detection."""
    # Test role account emails
    role_emails = [
        "admin@company.com",
        "support@service.net",
        "noreply@system.org",
        "info@business.com",
        "webmaster@site.com"
    ]
    for email in role_emails:
        result = check_role_account(email)
        assert result["is_role"]
        assert result["confidence"] > 0.8
        assert result["role_type"]

def test_regular_account_detection():
    """Test regular (non-role) account detection."""
    regular_emails = [
        "john.doe@company.com",
        "jane.smith@email.com",
        "user123@domain.org"
    ]
    for email in regular_emails:
        result = check_role_account(email)
        assert not result["is_role"]
        assert result["confidence"] > 0.8

def test_role_account_with_separators():
    """Test role accounts with various separators."""
    emails = [
        "customer.service@company.com",
        "tech-support@domain.com",
        "no_reply@system.org"
    ]
    for email in emails:
        result = check_role_account(email)
        assert result["is_role"]
        assert result["confidence"] > 0.7

def test_organizational_patterns():
    """Test organizational role patterns."""
    emails = [
        "dept.sales@company.com",
        "team.dev@organization.com",
        "dept.support@business.net"
    ]
    for email in emails:
        result = check_role_account(email)
        assert result["is_role"]
        assert result["role_type"] == "organizational"

def test_error_handling():
    """Test error handling for invalid inputs."""
    invalid_inputs = [
        "",
        "not-an-email",
        "@no-local-part.com",
        None
    ]
    for input in invalid_inputs:
        result = check_role_account(input)
        assert not result["is_role"]
        assert result["error"]