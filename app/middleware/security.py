"""Security middleware for adding security headers and CORS configuration."""
from typing import Dict, List, Optional
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline';"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )
        
        return response


def setup_cors(app: FastAPI, 
               allowed_origins: List[str],
               allowed_methods: List[str] = ["*"],
               allowed_headers: List[str] = ["*"],
               allow_credentials: bool = True,
               expose_headers: Optional[List[str]] = None) -> None:
    """Configure CORS for the application.
    
    Args:
        app: The FastAPI application instance
        allowed_origins: List of allowed origins (e.g. ["http://localhost:3000"])
        allowed_methods: List of allowed HTTP methods
        allowed_headers: List of allowed HTTP headers
        allow_credentials: Whether to allow credentials
        expose_headers: List of headers to expose to the browser
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        allow_credentials=allow_credentials,
        expose_headers=expose_headers or []
    )


def setup_security(app: FastAPI) -> None:
    """Configure security settings for the application.
    
    Args:
        app: The FastAPI application instance
    """
    # Add security middleware in order (most generic to most specific)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(SanitizerMiddleware)
    app.add_middleware(CSRFMiddleware, secret_key=settings.SECRET_KEY)
    app.add_middleware(SessionMiddleware)
    
    # Set up CORS
    setup_cors(app)
    
    # Add rate limiting
    app.add_middleware(
        BaseHTTPMiddleware,
        dispatch=RateLimitMiddleware(
            rate_limit=100,  # requests
            time_window=60   # seconds
        )
    )
    """Configure security middleware for the application."""
    app.add_middleware(SecurityHeadersMiddleware)