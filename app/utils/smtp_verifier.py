"""SMTP verification module for email validation.

This module provides SMTP-based email verification with proper error handling,
TLS support, and comprehensive result reporting.
"""
import smtplib
import socket
import logging
import ssl
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from .exceptions import SMTPVerificationError
from .metrics import ValidationTimer
from .dns_resolver import validate_dns

logger = logging.getLogger(__name__)

@dataclass
class SMTPResult:
    """Result of SMTP verification check."""
    valid: bool
    error: str = ""
    code: int = 0
    message: str = ""
    details: Dict = None
    supports_tls: bool = False

def verify_smtp(email: str) -> Dict:
    """Verify email existence using SMTP connection testing.
    
    Args:
        email: The email address to verify
        
    Returns:
        Dict containing verification results with fields:
            - valid (bool): Whether SMTP verification passed
            - error (str): Error message if verification failed
            - code (int): SMTP response code
            - message (str): SMTP response message
            - details (dict): Additional verification details
            - supports_tls (bool): Whether server supports TLS
    """
    with ValidationTimer():
        try:
            # First verify DNS
            dns_result = validate_dns(email)
            if not dns_result.get('valid', False):
                return SMTPResult(
                    valid=False,
                    error="DNS validation failed",
                    details=dns_result.get('details', {})
                ).__dict__

            domain = email.split('@')[1]
            mx_records = dns_result.get('details', {}).get('mx_records', [])
            
            if not mx_records:
                return SMTPResult(
                    valid=False,
                    error=f"No MX records found for domain: {domain}"
                ).__dict__

            # Try each MX server in priority order
            for priority, mx_host in sorted(mx_records):
                try:
                    result = _check_smtp_server(
                        email=email,
                        mx_host=mx_host,
                        domain=domain
                    )
                    if result.valid:
                        return result.__dict__
                except Exception as e:
                    logger.debug(f"SMTP check failed for {mx_host}: {str(e)}")
                    continue

            return SMTPResult(
                valid=False,
                error="All MX servers failed verification",
                details={"tried_servers": [mx[1] for mx in mx_records]}
            ).__dict__

        except Exception as e:
            logger.error(f"SMTP verification failed: {str(e)}")
            return SMTPResult(
                valid=False,
                error=f"Verification failed: {str(e)}"
            ).__dict__

def _check_smtp_server(email: str, mx_host: str, domain: str) -> SMTPResult:
    """Check email against specific SMTP server.
    
    Args:
        email: Email address to verify
        mx_host: MX server hostname
        domain: Email domain
        
    Returns:
        SMTPResult object with verification results
    """
    try:
        with smtplib.SMTP(timeout=10) as smtp:
            smtp.set_debuglevel(0)
            
            # Connect and say HELO
            logger.debug(f"Connecting to MX server: {mx_host}")
            smtp.connect(mx_host, 25)
            smtp.helo()
            
            # Check TLS support
            supports_tls = smtp.has_extn('starttls')
            if supports_tls:
                context = ssl.create_default_context()
                smtp.starttls(context=context)
                smtp.helo()  # Must send HELO again after STARTTLS
            
            # Send MAIL FROM
            # Use empty sender to reduce backscatter
            smtp.mail('')
            
            # Send RCPT TO
            code, message = smtp.rcpt(email)
            
            return SMTPResult(
                valid=(code == 250),
                code=code,
                message=message.decode() if isinstance(message, bytes) else message,
                supports_tls=supports_tls,
                details={
                    "mx_host": mx_host,
                    "domain": domain,
                    "response_code": code,
                    "response_message": message
                }
            )
            
    except (socket.timeout, smtplib.SMTPException) as e:
        raise SMTPVerificationError(f"SMTP verification failed for {mx_host}: {str(e)}")