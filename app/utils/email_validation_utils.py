"""Utility functions for email validation."""
from typing import Dict, List, Optional
import re
import dns.resolver
from app.utils.exceptions import ValidationError

def detect_typos(email: str) -> List[str]:
    """
    Detect potential typos in email address and suggest corrections.
    
    Args:
        email: The email address to check
        
    Returns:
        List of suggested corrections
    """
    common_domains = {
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'aol.com', 'icloud.com', 'protonmail.com'
    }
    
    suggestions = []
    local_part, domain = email.split('@')
    
    # Check for common domain typos
    for valid_domain in common_domains:
        if domain != valid_domain and len(domain) > 3:
            # Simple distance calculation
            distance = sum(1 for i in range(min(len(domain), len(valid_domain)))
                         if domain[i] != valid_domain[i])
            if distance <= 2:  # Allow up to 2 character differences
                suggestions.append(f"{local_part}@{valid_domain}")
    
    return suggestions

def detect_spam_trap(email: str) -> bool:
    """
    Check if email address appears to be a spam trap.
    
    Args:
        email: The email address to check
        
    Returns:
        True if email appears to be a spam trap
    """
    spam_trap_patterns = [
        r'^spam\.',
        r'^trap\.',
        r'\.trap@',
        r'\.spam@',
        r'^blackhole@',
        r'^honeypot@'
    ]
    
    return any(re.search(pattern, email.lower()) for pattern in spam_trap_patterns)

def detect_catch_all(email: str) -> bool:
    """
    Check if email address is a catch-all address.
    
    Args:
        email: The email address to check
        
    Returns:
        True if email appears to be a catch-all address
    """
    catch_all_patterns = [
        r'^all@',
        r'^catchall@',
        r'^.*@',
        r'^postmaster@'
    ]
    
    return any(re.search(pattern, email.lower()) for pattern in catch_all_patterns)

def detect_role_account(email: str) -> bool:
    """
    Check if email address is a role account.
    
    Args:
        email: The email address to check
        
    Returns:
        True if email is a role account
    """
    role_patterns = [
        r'^admin@',
        r'^support@',
        r'^info@',
        r'^sales@',
        r'^contact@',
        r'^webmaster@',
        r'^hostmaster@',
        r'^postmaster@'
    ]
    
    return any(re.search(pattern, email.lower()) for pattern in role_patterns)