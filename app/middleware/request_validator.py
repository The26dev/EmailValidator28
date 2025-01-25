"""Request validation middleware.

Provides centralized request validation, sanitization and transformation
for API endpoints.
"""
import json
import logging
import email_validator
from typing import Any, Dict, Optional
from email_validator import validate_email, EmailNotValidError
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.metrics import track_validation_error
from .error_handler import ErrorResponse

logger = logging.getLogger(__name__)

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for validating and sanitizing API requests."""
    
    async def dispatch(self, request: Request, call_next):
        """Process and validate request.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response with validated/sanitized data
            
        Raises:
            HTTPException for validation failures
        """
        try:
            # Get request body
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await self._get_request_body(request)
                if body:
                    # Validate content
                    await self._validate_request_content(request, body)
                    
                    # Transform request if needed
                    transformed = await self._transform_request(request, body)
                    if transformed != body:
                        # Update request with transformed data
                        setattr(request, "_json", transformed)
            
            # Validate headers
            await self._validate_headers(request)
            
            # Validate query params
            await self._validate_query_params(request)
            
            # Process request
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Request validation failed: {str(e)}")
            # Track validation errors
            track_validation_error(str(e))
            
            error = ErrorResponse(
                status_code=400,
                message=str(e),
                error_code="REQUEST_VALIDATION_ERROR",
                details={
                    "error": str(e),
                    "request_path": request.url.path,
                    "request_method": request.method
                }
            )
            return JSONResponse(
                status_code=400,
                content=error.body
            )
    
    async def _get_request_body(self, request: Request) -> Optional[Dict]:
        """Get and parse request body.
        
        Args:
            request: FastAPI request
            
        Returns:
            Parsed request body or None
        """
        try:
            body = await request.json()
            return body
        except:
            return None
    
    async def _validate_request_content(
        self,
        request: Request,
        body: Dict
    ) -> None:
        """Validate request content based on endpoint.
        
        Args:
            request: FastAPI request
            body: Request body to validate
            
        Raises:
            ValueError for validation failures
        """
        path = request.url.path
        method = request.method
        
        if path == "/validate/email" and method == "POST":
            await self._validate_single_email_request(body)
        elif path == "/validate/batch" and method == "POST":
            await self._validate_batch_email_request(body)
    
    async def _validate_single_email_request(self, body: Dict) -> None:
        """Validate single email validation request.
        
        Args:
            body: Request body
            
        Raises:
            ValueError if validation fails
        """
        if not isinstance(body, dict):
            raise ValueError("Request body must be a JSON object")
            
        email = body.get("email")
        if not email:
            raise ValueError("Missing required field: email")
            
        try:
            validate_email(email)
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email format: {str(e)}")
            
        options = body.get("options", {})
        if options and not isinstance(options, dict):
            raise ValueError("Options must be a JSON object")
    
    async def _validate_batch_email_request(self, body: Dict) -> None:
        """Validate batch email validation request.
        
        Args:
            body: Request body
            
        Raises:
            ValueError if validation fails
        """
        if not isinstance(body, dict):
            raise ValueError("Request body must be a JSON object")
            
        emails = body.get("emails")
        if not emails:
            raise ValueError("Missing required field: emails")
            
        if not isinstance(emails, list):
            raise ValueError("Emails must be an array")
            
        if len(emails) > 100:
            raise ValueError("Maximum batch size exceeded (limit: 100)")
            
        for email in emails:
            try:
                validate_email(email)
            except EmailNotValidError as e:
                raise ValueError(f"Invalid email format for {email}: {str(e)}")
                
        options = body.get("options", {})
        if options and not isinstance(options, dict):
            raise ValueError("Options must be a JSON object")
    
    async def _validate_headers(self, request: Request) -> None:
        """Validate request headers.
        
        Args:
            request: FastAPI request
            
        Raises:
            ValueError for invalid headers
        """
        # Validate content type for requests with body
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                raise ValueError(
                    "Invalid Content-Type. Expected: application/json"
                )
    
    async def _validate_query_params(self, request: Request) -> None:
        """Validate query parameters.
        
        Args:
            request: FastAPI request
            
        Raises:
            ValueError for invalid parameters
        """
        # Add custom query parameter validation logic here
        pass
    
    async def _transform_request(
        self,
        request: Request,
        body: Dict
    ) -> Dict:
        """Transform request data if needed.
        
        Args:
            request: FastAPI request
            body: Request body
            
        Returns:
            Transformed request data
        """
        # Add request transformation logic here
        return body