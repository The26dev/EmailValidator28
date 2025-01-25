"""Authentication module for API key and JWT token management.

This module provides functionality for:
- Generating and validating API keys
- JWT token handling and validation
- Key rotation mechanisms
- Integration with rate limiting
"""

import secrets
import jwt
import datetime
from typing import Set, Dict, Optional
from .rate_limiter import RateLimiter
from .logger import logger
from .exceptions import AuthenticationError
from ..database import get_db_session
from ..models import APIKey

# Configuration
JWT_SECRET = "your-secret-key"  # Should be loaded from environment variables
JWT_ALGORITHM = "HS256"
API_KEY_LENGTH = 32
KEY_ROTATION_DAYS = 90

def generate_api_key() -> str:
    """Generate a new API key.
    
    Returns:
        str: A new API key
    """
    api_key = secrets.token_urlsafe(API_KEY_LENGTH)
    with get_db_session() as session:
        new_key = APIKey(
            key=api_key,
            created_at=datetime.datetime.utcnow(),
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=KEY_ROTATION_DAYS)
        )
        session.add(new_key)
        session.commit()
    logger.info(f"Generated new API key")
    return api_key

def validate_api_key(api_key: str) -> bool:
    """Validate an API key.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not api_key:
        logger.warning("Empty API key provided")
        return False
        
    with get_db_session() as session:
        key_record = session.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.revoked == False,
            APIKey.expires_at > datetime.datetime.utcnow()
        ).first()
        
        if not key_record:
            logger.warning("Invalid or expired API key")
            return False
            
        # Check rate limits
        rate_limiter = RateLimiter()
        if not rate_limiter.check_rate_limit(api_key):
            logger.warning("Rate limit exceeded for API key")
            return False
            
        return True

def revoke_api_key(api_key: str) -> bool:
    """Revoke an API key.
    
    Args:
        api_key: The API key to revoke
        
    Returns:
        bool: True if successfully revoked, False otherwise
    """
    with get_db_session() as session:
        key_record = session.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.revoked == False
        ).first()
        
        if not key_record:
            logger.warning("Attempted to revoke non-existent API key")
            return False
            
        key_record.revoked = True
        key_record.revoked_at = datetime.datetime.utcnow()
        session.commit()
        logger.info("API key revoked successfully")
        return True

def generate_jwt_token(api_key: str) -> Optional[str]:
    """Generate a JWT token for an API key.
    
    Args:
        api_key: The API key to generate a token for
        
    Returns:
        Optional[str]: JWT token if successful, None otherwise
    """
    if not validate_api_key(api_key):
        logger.warning("Failed to generate JWT token - invalid API key")
        return None
        
    payload = {
        'api_key': api_key,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        'iat': datetime.datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logger.info("Generated new JWT token")
    return token

def validate_jwt_token(token: str) -> bool:
    """Validate a JWT token.
    
    Args:
        token: The JWT token to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return validate_api_key(payload['api_key'])
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token")
        return False

def list_valid_keys() -> Set[str]:
    """List all valid API keys.
    
    Returns:
        Set[str]: Set of valid API keys
    """
    with get_db_session() as session:
        valid_keys = session.query(APIKey).filter(
            APIKey.revoked == False,
            APIKey.expires_at > datetime.datetime.utcnow()
        ).all()
        return {key.key for key in valid_keys}

def rotate_api_key(old_api_key: str) -> Optional[str]:
    """Rotate an API key by generating a new one and revoking the old one.
    
    Args:
        old_api_key: The API key to rotate
        
    Returns:
        Optional[str]: New API key if successful, None otherwise
    """
    if not validate_api_key(old_api_key):
        logger.warning("Cannot rotate invalid API key")
        return None
        
    new_api_key = generate_api_key()
    if revoke_api_key(old_api_key):
        logger.info("API key rotated successfully")
        return new_api_key
    return None