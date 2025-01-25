import re
import dns.resolver
from typing import Dict, Any, Optional, List
from .dns_resolver import resolve_mx_records
from .disposable_email_detector import check_disposable_email
from .domain_reputation_checker import check_domain_reputation
from .typo_detector import detect_typos
from .spam_trap_detector import detect_spam_trap
from .catch_all_detector import detect_catch_all
from .role_account_detector import detect_role_account
from .error_handler import ValidationFailedError

class EmailValidator:
    """Comprehensive email validation with multiple checks."""
    
    def __init__(self):
        self.email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
    def validate_email(self, email: str, deep_validation: bool = False) -> Dict[str, Any]:
        """
        Validate an email address with multiple checks.
        
        Args:
            email: The email address to validate
            deep_validation: Whether to perform additional deep validation checks
        
        Returns:
            Dict containing validation results and metadata
        """
        try:
            result = {
                'email': email,
                'is_valid': False,
                'checks': {},
                'reasons': [],
                'metadata': {}
            }
            
            # Basic syntax validation
            if not self._validate_syntax(email):
                result['reasons'].append('Invalid email syntax')
                return result
            
            # Split email into parts
            local_part, domain = email.split('@')
            result['metadata']['local_part'] = local_part
            result['metadata']['domain'] = domain
            
            # Domain checks
            mx_records = resolve_mx_records(domain)
            if not mx_records:
                result['reasons'].append('No MX records found')
                result['checks']['has_mx_records'] = False
                return result
            
            result['checks']['has_mx_records'] = True
            result['metadata']['mx_records'] = mx_records
            
            # Disposable email check
            is_disposable = check_disposable_email(domain)
            result['checks']['is_disposable'] = is_disposable
            if is_disposable:
                result['reasons'].append('Disposable email service detected')
            
            # Reputation check
            reputation = check_domain_reputation(domain)
            result['checks']['reputation'] = reputation
            result['metadata']['reputation_score'] = reputation.get('score')
            
            if reputation.get('score', 0) < 50:
                result['reasons'].append('Poor domain reputation')
            
            if deep_validation:
                self._perform_deep_validation(email, result)
            
            # Final validity determination
            result['is_valid'] = (
                not is_disposable and
                reputation.get('score', 0) >= 50 and
                not result.get('checks', {}).get('is_role_account', False) and
                not result.get('checks', {}).get('is_spam_trap', False)
            )
            
            return result
        
        except Exception as e:
            raise ValidationFailedError(f"Email validation failed: {str(e)}")
    
    def validate_bulk(self, emails: List[str], deep_validation: bool = False) -> List[Dict[str, Any]]:
        """Validate multiple email addresses."""
        return [self.validate_email(email, deep_validation) for email in emails]
    
    def _validate_syntax(self, email: str) -> bool:
        """Validate email syntax using regex."""
        if not email or not isinstance(email, str):
            return False
        return bool(self.email_regex.match(email))
    
    def _perform_deep_validation(self, email: str, result: Dict[str, Any]) -> None:
        """Perform additional validation checks including typo detection, spam traps, and role accounts."""
        try:
            # Typo detection
            typos = detect_typos(email)
            if typos:
                result['checks']['possible_typos'] = typos
                result['metadata']['suggested_corrections'] = typos
                result['reasons'].append(f"Possible typo detected. Did you mean: {', '.join(typos)}?")
            
            # Spam trap detection
            is_spam_trap = detect_spam_trap(email)
            result['checks']['is_spam_trap'] = is_spam_trap
            if is_spam_trap:
                result['reasons'].append('Potential spam trap detected')
                result['metadata']['risk_level'] = 'high'
            
            # Catch-all detection
            is_catch_all = detect_catch_all(email)
            result['checks']['is_catch_all'] = is_catch_all
            result['metadata']['catch_all'] = is_catch_all
            if is_catch_all:
                result['reasons'].append('Catch-all email address detected')
                result['metadata']['risk_level'] = 'medium'
            
            # Role account detection
            is_role = detect_role_account(email)
            result['checks']['is_role_account'] = is_role
            if is_role:
                result['reasons'].append('Role account detected')
                result['metadata']['risk_level'] = 'low'
            
            # Update validation score based on deep validation results
            validation_score = 100
            if is_spam_trap:
                validation_score -= 50
            if is_catch_all:
                validation_score -= 30
            if is_role:
                validation_score -= 20
            if typos:
                validation_score -= 10
            
            result['metadata']['validation_score'] = validation_score
            
        except Exception as e:
            result['metadata']['deep_validation_error'] = str(e)
            result['reasons'].append(f"Deep validation failed: {str(e)}")
            raise ValidationError(f"Deep validation failed: {str(e)}")
    
    def get_validation_report(self, email: str) -> Dict[str, Any]:
        """Generate a detailed validation report."""
        result = self.validate_email(email, deep_validation=True)
        
        return {
            'validation_result': result,
            'timestamp': datetime.now().isoformat(),
            'validation_level': 'deep' if result.get('checks', {}).get('possible_typos') is not None else 'basic',
            'summary': {
                'is_valid': result['is_valid'],
                'total_checks': len(result['checks']),
                'failed_checks': len(result['reasons'])
            }
        }

# Create singleton instance
email_validator = EmailValidator()