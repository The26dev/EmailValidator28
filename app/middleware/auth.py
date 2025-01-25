"""JWT Authentication middleware implementation."""
from typing import List, Optional

from .auth_config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    JWT_SECRET,
    AuthenticationError,
    AuthorizationError,
    datetime,
    jwt,
    request,
    timedelta,
    wraps,
)

def create_access_token(user_id: str, roles: Optional[List[str]] = None) -> str:
    """Create a short-lived access token."""
    if roles is None:
        roles = []
    payload = {
        'user_id': user_id,
        'roles': roles,
        'token_type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    """Create a long-lived refresh token."""
    payload = {
        'user_id': user_id,
        'token_type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def requires_auth(f):
    """Decorator to require valid JWT access token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            raise AuthenticationError("Missing authentication token")
        
        try:
            # Verify token
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )
            
            # Verify token type
            if payload.get('token_type') != 'access':
                raise AuthenticationError("Invalid token type")
            
            # Store user info in request context
            request.user_id = payload['user_id']
            request.user_roles = payload.get('roles', [])
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
            
        return f(*args, **kwargs)
    return decorated

def requires_roles(roles: List[str]):
    """Decorator to require specific roles in JWT access token."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'user_roles'):
                raise AuthenticationError("Missing role information")
                
            # Check for superadmin role which has all permissions
            if 'superadmin' in request.user_roles:
                return f(*args, **kwargs)
                
            # Check for required roles
            if not any(role in request.user_roles for role in roles):
                raise AuthorizationError("Insufficient permissions")
                
            return f(*args, **kwargs)
        return decorated
    return decorator

def refresh_access_token(refresh_token: str) -> str:
    """Refresh an access token using a valid refresh token.
    
    Args:
        refresh_token: The refresh token to use
        
    Returns:
        str: A new access token
        
    Raises:
        AuthenticationError: If refresh token is invalid
    """
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get('token_type') != 'refresh':
            raise AuthenticationError("Invalid token type")
            
        user_id = payload.get('user_id')
        if not user_id:
            raise AuthenticationError("Invalid token payload")
            
        return create_access_token(user_id)
    except JWTError:
        raise AuthenticationError("Invalid refresh token")
    """Create new access token using refresh token."""
    try:
        # Verify refresh token
        payload = jwt.decode(
            refresh_token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        
        # Verify token type
        if payload.get('token_type') != 'refresh':
            raise jwt.InvalidTokenError("Invalid token type")
        
        # Get user information from database
        user_id = payload['user_id']
        user = get_user_from_database(user_id)  # Implement this function
        
        # Create new access token
        return create_access_token(user_id, user.get('roles', []))
        
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Refresh token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid refresh token")

def get_token_from_request() -> Optional[str]:
    """Extract JWT token from request header or cookie."""
    # Try to get from Authorization header first
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            auth_type, token = auth_header.split()
            if auth_type.lower() == 'bearer':
                return token
        except ValueError:
            pass
            
    # Then try to get from cookie
    return request.cookies.get('access_token')

def set_refresh_token_cookie(response, refresh_token: str) -> None:
    """Set refresh token as httpOnly cookie."""
    max_age = JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # Convert days to seconds
    response.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,
        secure=True,  # Requires HTTPS
        samesite='Strict',
        max_age=max_age
    )