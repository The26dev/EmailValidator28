"""
Role Account Detector Module
Identifies role-based email addresses that are often targets for abuse.
"""

ROLE_BASED_PREFIXES = [
    "admin", "support", "info", "contact", "sales", "help",
    "service", "billing", "noreply", "no-reply", "webmaster"
]

def normalize_local_part(email: str) -> Optional[str]:
    """Normalize the local part of email for consistent matching.
    
    Args:
        email: Email address to normalize
        
    Returns:
        Normalized local part or None if invalid
    """
    try:
        # Extract local part
        local = email.split("@")[0].lower()
        
        # Remove common separators
        local = re.sub(r'[._-]', '', local)
        
        return local
    except:
        return None

def match_role_pattern(local_part: str) -> Tuple[bool, float, str]:
    """Match local part against role patterns.
    
    Args:
        local_part: Normalized local part to check
        
    Returns:
        Tuple of (is_match, confidence, role_type)
    """
    for category, pattern in ROLE_PATTERNS.items():
        for prefix in pattern["prefixes"]:
            if local_part.startswith(prefix):
                return True, pattern["confidence"], pattern["type"]
            if local_part.endswith(prefix):
                return True, pattern["confidence"] * 0.8, pattern["type"]
            if prefix in local_part:
                return True, pattern["confidence"] * 0.6, pattern["type"]
                
    return False, 0.0, ""

def check_role_account(email: str) -> Dict:
    """Determines if the email address is a role-based account.
    
    Uses pattern matching and heuristic approaches to detect role-based
    email accounts like admin@, support@, etc.
    
    Args:
        email: Email address to check
        
    Returns:
        Dict containing role assessment with fields:
            - is_role (bool): Whether email is role-based
            - confidence (float): Confidence level of assessment (0-1)
            - role_type (str): Type of role account if detected
            - error (str): Error message if check failed
    """
    try:
        # Validate input
        if not email or "@" not in email:
            return {
                "is_role": False,
                "confidence": 1.0,
                "role_type": "",
                "error": "Invalid email format"
            }
            
        # Normalize local part
        local_part = normalize_local_part(email)
        if not local_part:
            return {
                "is_role": False,
                "confidence": 1.0,
                "role_type": "",
                "error": "Could not parse local part"
            }
            
        # Check for role patterns
        is_role, confidence, role_type = match_role_pattern(local_part)
        
        # Additional checks to adjust confidence
        if is_role:
            # Length-based adjustment
            if len(local_part) > 30:
                confidence *= 0.7  # Longer addresses less likely to be roles
                
            # Number-based adjustment
            if re.search(r'\d', local_part):
                confidence *= 0.8  # Numbers less common in role accounts
                
            # Common name check
            if any(name in local_part for name in ["john", "david", "mike", "sarah", "lisa"]):
                confidence *= 0.5  # Common names less likely to be roles
        
        return {
            "is_role": is_role,
            "confidence": round(confidence, 2),
            "role_type": role_type if is_role else "",
            "error": ""
        }
        
    except Exception as e:
        logger.error(f"Role account check failed: {str(e)}")
        return {
            "is_role": False,
            "confidence": 0.0,
            "role_type": "",
            "error": f"Check failed: {str(e)}"
        }
    """
    Determines if the email address is a role-based account.
    
    Args:
        email (str): The email address to evaluate.
    
    Returns:
        bool: True if it's a role account, False otherwise.
    """
    local_part = email.split('@')[0].lower()
    return any(local_part.startswith(prefix) for prefix in ROLE_BASED_PREFIXES)