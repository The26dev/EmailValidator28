"""CSRF protection middleware."""

import secrets
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware for CSRF protection."""
    
    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.secret_key = secret_key
        
    def generate_csrf_token(self) -> str:
        """Generate a new CSRF token."""
        return secrets.token_urlsafe(32)
        
    def verify_csrf_token(self, request_token: Optional[str], session_token: Optional[str]) -> bool:
        """Verify that the request token matches the session token."""
        if not request_token or not session_token:
            return False
        return secrets.compare_digest(request_token, session_token)
        
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method in ['GET', 'HEAD', 'OPTIONS', 'TRACE']:
            # Safe methods don't need CSRF protection
            response = await call_next(request)
            
            # Generate new token for forms
            if hasattr(request.state, 'session'):
                csrf_token = self.generate_csrf_token()
                request.state.session['csrf_token'] = csrf_token
                response.set_cookie(
                    'csrf_token',
                    csrf_token,
                    httponly=True,
                    secure=True,
                    samesite='strict'
                )
            return response
            
        # For unsafe methods, verify CSRF token
        request_token = request.headers.get('X-CSRF-Token')
        if not request_token:
            request_token = request.cookies.get('csrf_token')
            
        session_token = None
        if hasattr(request.state, 'session'):
            session_token = request.state.session.get('csrf_token')
            
        if not self.verify_csrf_token(request_token, session_token):
            raise HTTPException(status_code=403, detail="Invalid CSRF token")