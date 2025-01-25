"""Email validation service implementation."""

import re
from typing import Dict, Tuple

from app.validation.dns_validator import dns_validator, DNSValidationError

class EmailValidationError(Exception):
    """Custom exception for email validation errors."""
    pass

class EmailValidator:
    """Email address validator."""
    
    # RFC 5322 email regex pattern
    EMAIL_PATTERN = re.compile(r'''(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])''')
    
    async def validate_email(self, email: str) -> Tuple[bool, Dict[str, bool]]:
        """Validate an email address.
        
        Args:
            email: The email address to validate
            
        Returns:
            Tuple[bool, Dict[str, bool]]: Tuple of (is_valid, validation_results)
            
        Raises:
            EmailValidationError: If validation fails due to an error
        """
        results = {
            'format_valid': False,
            'dns_valid': False,
            'mx_found': False
        }
        
        # Check email format
        if not self.EMAIL_PATTERN.match(email):
            return False, results
            
        results['format_valid'] = True
        
        try:
            # Split email into local part and domain
            local_part, domain = email.rsplit('@', 1)
            
            # Validate domain
            domain_valid = await dns_validator.validate_domain(domain)
            results['dns_valid'] = domain_valid
            
            if domain_valid:
                # Check MX records
                mx_records = await dns_validator.get_mx_records(domain)
                results['mx_found'] = bool(mx_records)
                
            return all(results.values()), results
            
        except DNSValidationError as e:
            raise EmailValidationError(f"DNS validation failed: {str(e)}")
        except Exception as e:
            raise EmailValidationError(f"Email validation failed: {str(e)}")

# Global email validator instance
email_validator = EmailValidator()