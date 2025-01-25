"""Email validation orchestrator module."""
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from functools import wraps
import asyncio

from app.utils.syntax_validator import validate_syntax
from app.utils.email_dns_validator import EmailDNSValidator
from app.utils.cache_manager import CacheManager
from app.utils.smtp_verifier import verify_smtp
from app.utils.disposable_email_detector import is_disposable_email
from app.utils.role_account_detector import is_role_account
from app.utils.typo_detector import detect_typo
from app.utils.domain_reputation import get_domain_reputation
from app.utils.spam_trap_detector import SpamTrapDetector
from app.utils.catch_all_detector import CatchAllDetector
from app.utils.exceptions import ValidationError
from app.utils.risk_score import calculate_risk_score
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
import asyncio

# Initialize components
spam_trap_detector = SpamTrapDetector()
catch_all_detector = CatchAllDetector()
cache_manager = CacheManager()
dns_validator = EmailDNSValidator(cache_manager=cache_manager)

async def validate_email(email: str) -> Dict:
    """Validate an email address using multiple validation steps.

    Performs:
    - Syntax validation 
    - DNS validation including MX, A/AAAA, PTR records
    - Domain reputation checks
    - Disposable email detection
    - Anti-spam checks
    - Result caching
    - International email support
    
    Args:
        email (str): The email address to validate.
        
    Returns:
        dict: Validation results including:
            - is_valid: bool indicating if email is valid
            - checks: dict of all validation results
            - score: int (0-100) indicating confidence score
            - error: str containing error message if validation fails
            
    Raises:
        ValidationError: If email format is invalid or validation fails
        RateLimitExceeded: If domain exceeds rate limit
    """
    # Initialize results dictionary with default values
    results = {
        "email": email,
        "is_valid": False,
        "checks": {
            "syntax": {"is_valid": False},
            "dns": {},
            "disposable": {"is_disposable": False},
            "role_account": {"is_role": False},
            "spam_trap": {"is_trap": False},
            "catch_all": {"is_catch_all": False},
            "typos": {"suggestions": []},
            "reputation": {"score": 0}
        },
        "score": 0,
        "error": None
    }
    
    try:
        domain = extract_domain(email)
    except ValidationError as e:
        results["error"] = str(e)
        return results
    
    # Syntax Validation
    try:
        if not validate_syntax(email):
            results["error"] = "Invalid email syntax"
            return results
        results["checks"]["syntax"]["is_valid"] = True
    except Exception as e:
        logger.error(f"Syntax validation failed for {email}: {str(e)}")
        results["error"] = f"Syntax validation error: {str(e)}"
        return results

    # DNS Validation
    try:
        dns_results = await dns_validator.validate_domain(domain)
        results["checks"]["dns"] = dns_results
        
        if not dns_results.get("has_mx") and not dns_results.get("has_a"):
            results["error"] = "Domain has no valid mail servers"
            return results
    except RateLimitExceeded as e:
        logger.warning(f"Rate limit exceeded for {email}: {str(e)}")
        results["error"] = f"Rate limit exceeded: {str(e)}"
        return results
    except ValidationError as e:
        logger.error(f"DNS validation failed for {email}: {str(e)}")
        results["error"] = f"DNS validation error: {str(e)}"
        return results
    
    # Additional Validation Steps
    try:
        # SMTP Verification
        smtp_result = await verify_smtp(domain)
        results["checks"]["smtp"] = {"verified": smtp_result}
        
        # Disposable Email Check
        is_disposable = await is_disposable_email(email)
        results["checks"]["disposable"]["is_disposable"] = is_disposable
        
        # Role Account Detection
        is_role = is_role_account(email)
        results["checks"]["role_account"]["is_role"] = is_role
        
        # Check for typos
        typo_suggestions = detect_typo(email)
        if typo_suggestions:
            results["checks"]["typos"]["suggestions"] = typo_suggestions
        
        # Get domain reputation
        reputation = await get_domain_reputation(domain)
        results["checks"]["reputation"]["score"] = reputation
        
        # Check for spam traps
        is_spam_trap = await spam_trap_detector.check(email)
        results["checks"]["spam_trap"]["is_trap"] = is_spam_trap
        
        # Check for catch-all
        is_catch_all = await catch_all_detector.check(domain)
        results["checks"]["catch_all"]["is_catch_all"] = is_catch_all
        
        # Calculate overall validity and score
        results["is_valid"] = (
            results["checks"]["syntax"]["is_valid"] and
            dns_results.get("has_mx", False) and 
            not results["checks"]["disposable"]["is_disposable"] and
            not results["checks"]["spam_trap"]["is_trap"]
        )
        
        results["score"] = calculate_risk_score(results)
        
        return results
        
    except Exception as e:
        logger.error(f"Validation failed for {email}: {str(e)}")
        results["error"] = f"Validation error: {str(e)}"
        return results
    return results
    
    # Risk Scoring
    result["risk_score"] = calculate_risk_score(result)
    
    # Final Status
    result["status"] = "Valid" if result["risk_score"] < 50 else "Risky"
    
    return result

async def validate_emails_batch(emails: List[str], batch_size: int = 50) -> Dict[str, Any]:
    """
    Validates multiple email addresses in parallel batches.
    
    Args:
        emails (List[str]): List of email addresses to validate.
        batch_size (int): Size of each batch for parallel processing.
    
    Returns:
        Dict: Dictionary containing results list and summary statistics.
    """
    if not emails:
        return {
            "results": [],
            "summary": {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "errors": 0
            }
        }
    
    results = []
    async def process_batch(batch: List[str]) -> List[Dict]:
        tasks = []
        for email in batch:
            tasks.append(asyncio.create_task(validate_email(email)))
        
        batch_results = []
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        for email, result in zip(batch, completed_tasks):
            if isinstance(result, Exception):
                error_result = {
                    "email": email,
                    "is_valid": False,
                    "status": "Error",
                    "error": str(result)
                }
                batch_results.append(error_result)
            else:
                batch_results.append(result)
        return batch_results
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            batch_results = list(executor.map(process_email, batch))
            results.extend(batch_results)
            
            # Small delay between batches to prevent rate limiting
            if i + batch_size < len(emails):
                await asyncio.sleep(0.1)
    
    return results

def extract_domain(email: str) -> str:
    """
    Extracts the domain part from the email address.
    
    Args:
        email (str): The email address.
    
    Returns:
        str: The domain if extraction is successful, else an empty string.
    """
    try:
        return email.split('@')[1].lower()
    except IndexError:
        return ""

def calculate_risk_score(validation_result: Dict) -> int:
    """
    Calculates a risk score based on various validation factors.
    
    Args:
        validation_result (dict): Results from validation steps.
    
    Returns:
        int: Calculated risk score between 0-100.
    """
    score = 0
    
    # Core validations (heavily weighted)
    if not validation_result["syntax_valid"]:
        score += 40
    if not validation_result["domain_exists"]:
        score += 40
    if not validation_result["mx_records_valid"]:
        score += 30
    if not validation_result["smtp_verified"]:
        score += 20
        
    # Additional security checks
    if not validation_result["has_ptr"]:
        score += 10
    if validation_result["disposable"]:
        score += 15
    if validation_result["role_account"]:
        score += 5
    if validation_result["spam_trap"]:
        score += 40
    if validation_result["catch_all"]:
        score += 10
        
    # Domain reputation factor (0-100 scale, inversely proportional)
    reputation_factor = (100 - validation_result["domain_reputation"]) * 0.2
    score += reputation_factor
    
    # Cap the score at 100
    return min(100, score)