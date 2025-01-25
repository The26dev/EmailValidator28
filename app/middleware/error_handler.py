"""Error handling middleware.

Provides centralized error handling and consistent error response formatting
for all API endpoints.
"""
import logging
import traceback
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException

from ..utils.exceptions import (
    ValidationError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
    ServiceError
)
from ..utils.error_tracking import track_error

logger = logging.getLogger(__name__)

ERROR_RESPONSES = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout"
}

class ErrorResponse:
    """Standardized error response structure."""
    
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        self.status_code = status_code
        self.body = {
            "error": {
                "code": error_code or ERROR_RESPONSES.get(status_code, "UNKNOWN_ERROR"),
                "message": message,
                "details": details or {}
            }
        }

def setup_error_handlers(app: FastAPI) -> None:
    """Configure error handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        status_code = exc.status_code
        message = str(exc.detail)
        
        # Track error metrics
        track_error(
            error_type="http_error",
            error_message=message,
            additional_context={
                "status_code": status_code,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        error = ErrorResponse(
            status_code=status_code,
            message=message
        )
        
        return JSONResponse(
            status_code=status_code,
            content=error.body
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        status_code = 400
        
        # Format validation errors
        details = []
        for error in exc.errors():
            details.append({
                "field": " -> ".join([str(x) for x in error["loc"]]),
                "message": error["msg"],
                "type": error["type"]
            })
            
        error = ErrorResponse(
            status_code=status_code,
            message="Request validation failed",
            error_code="VALIDATION_ERROR",
            details={"validation_errors": details}
        )
        
        # Track validation errors
        track_error(status_code, request.url.path, "validation_error")
        
        return JSONResponse(
            status_code=status_code,
            content=error.body
        )

    @app.exception_handler(ValidationError)
    async def custom_validation_error_handler(request: Request, exc: ValidationError):
        """Handle custom validation errors."""
        status_code = 400
        message = str(exc)
        
        error = ErrorResponse(
            status_code=status_code,
            message=message,
            error_code="EMAIL_VALIDATION_ERROR"
        )
        
        track_error(status_code, request.url.path, "email_validation_error")
        
        return JSONResponse(
            status_code=status_code,
            content=error.body
        )

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError):
        """Handle authentication errors."""
        status_code = 401
        message = str(exc)
        
        error = ErrorResponse(
            status_code=status_code,
            message=message,
            error_code="AUTHENTICATION_ERROR"
        )
        
        track_error(status_code, request.url.path, "auth_error")
        
        return JSONResponse(
            status_code=status_code,
            content=error.body
        )

    @app.exception_handler(RateLimitError)
    async def rate_limit_error_handler(request: Request, exc: RateLimitError):
        """Handle rate limit errors."""
        status_code = 429
        message = str(exc)
        
        error = ErrorResponse(
            status_code=status_code,
            message=message,
            error_code="RATE_LIMIT_EXCEEDED"
        )
        
        track_error(status_code, request.url.path, "rate_limit_error")
        
        return JSONResponse(
            status_code=status_code,
            content=error.body,
            headers={"Retry-After": "60"}
        )

    @app.exception_handler(ResourceNotFoundError)
    async def not_found_error_handler(request: Request, exc: ResourceNotFoundError):
        """Handle resource not found errors."""
        status_code = 404
        message = str(exc)
        
        error = ErrorResponse(
            status_code=status_code,
            message=message,
            error_code="RESOURCE_NOT_FOUND"
        )
        
        track_error(status_code, request.url.path, "not_found_error")
        
        return JSONResponse(
            status_code=status_code,
            content=error.body
        )

    @app.exception_handler(ServiceError)
    async def service_error_handler(request: Request, exc: ServiceError):
        """Handle service-level errors."""
        status_code = 500
        message = str(exc)
        
        error = ErrorResponse(
            status_code=status_code,
            message=message,
            error_code="SERVICE_ERROR",
            details={"error_details": exc.details} if hasattr(exc, "details") else None
        )
        
        # Log internal errors
        logger.error(
            f"Service error occurred: {message}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
                "error_details": error.body
            }
        )
        
        track_error(
            error_type="service_error",
            error_message=message,
            additional_context={
                "status_code": status_code,
                "path": request.url.path,
                "method": request.method,
                "error_details": error.body
            }
        )
        
        return JSONResponse(
            status_code=status_code,
            content=error.body
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        """Handle any unhandled exceptions."""
        status_code = 500
        message = "An unexpected error occurred"
        
        # Log unhandled errors
        logger.error(
            f"Unhandled error occurred: {str(exc)}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc()
            }
        )
        
        error = ErrorResponse(
            status_code=status_code,
            message=message,
            error_code="INTERNAL_ERROR"
        )
        
        track_error(status_code, request.url.path, "unhandled_error")
        
        return JSONResponse(
            status_code=status_code,
            content=error.body
        )