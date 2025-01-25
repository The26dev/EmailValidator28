"""
Syntax Validator Module
Provides functionality to validate email syntax.
"""

import re
from app.utils.exceptions import ValidationError

def validate_syntax(email: str) -> bool:
    """
    Validates the email syntax based on RFC 5322 standards.
    
    Args:
        email (str): The email address to validate.
    
    Returns:
        bool: True if syntax is valid, False otherwise.
    
    Raises:
        ValidationError: If the email syntax is invalid.
    """
    # RFC 5322 Official Standard Regex
    regex = r"(^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+" \
            r"@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$)"
    
    if re.match(regex, email):
        return True
    else:
        raise ValidationError("Invalid email syntax.")