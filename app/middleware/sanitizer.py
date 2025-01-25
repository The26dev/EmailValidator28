"""Input sanitization and XSS protection middleware."""

import html
import re
from typing import Any, Dict, Union

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class InputSanitizer:
    """Utility class for sanitizing input data."""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize a string value."""
        # HTML escape
        value = html.escape(value)
        # Remove potential script tags that might have been escaped
        value = re.sub(r'&lt;script.*?&gt;.*?&lt;/script&gt;', '', value, flags=re.DOTALL)
        return value
    
    @staticmethod
    def sanitize_value(value: Any) -> Any:
        """Sanitize a value based on its type."""
        if isinstance(value, str):
            return InputSanitizer.sanitize_string(value)
        elif isinstance(value, dict):
            return InputSanitizer.sanitize_dict(value)
        elif isinstance(value, list):
            return [InputSanitizer.sanitize_value(item) for item in value]
        return value
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize all string values in a dictionary."""
        return {k: InputSanitizer.sanitize_value(v) for k, v in data.items()}

class SanitizerMiddleware(BaseHTTPMiddleware):
    """Middleware for sanitizing request data and protecting against XSS."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Copy request object to avoid modifying the original
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                # Get request body
                body = await request.json()
                # Sanitize the body
                sanitized_body = InputSanitizer.sanitize_dict(body)
                # Store sanitized body in request state
                request.state.sanitized_body = sanitized_body
            except ValueError:
                # If body is not JSON, continue without sanitizing
                pass
        
        # Get query parameters and sanitize them
        query_params = dict(request.query_params)
        sanitized_query = InputSanitizer.sanitize_dict(query_params)
        request.state.sanitized_query = sanitized_query
        
        response = await call_next(request)
        
        # Add security headers
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response