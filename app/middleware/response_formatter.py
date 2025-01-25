"""Response formatting middleware.

Provides consistent response formatting and standardization for all API responses.
Adds metadata, request IDs, and standardizes the structure.
"""
import time
import uuid
import logging
from typing import Any, Dict, Optional
from datetime import datetime

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.metrics import track_response_time

logger = logging.getLogger(__name__)

class ResponseMetadata:
    """Standard metadata for API responses."""
    
    def __init__(
        self,
        request_id: str,
        path: str,
        timestamp: str,
        duration_ms: float
    ):
        self.request_id = request_id
        self.path = path
        self.timestamp = timestamp
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict:
        """Convert metadata to dictionary."""
        return {
            "request_id": self.request_id,
            "path": self.path,
            "timestamp": self.timestamp,
            "duration_ms": round(self.duration_ms, 2)
        }

class FormattedResponse:
    """Standardized API response format."""
    
    def __init__(
        self,
        data: Any,
        metadata: ResponseMetadata,
        status_code: int = 200,
        message: Optional[str] = None,
        links: Optional[Dict] = None
    ):
        self.data = data
        self.metadata = metadata
        self.status_code = status_code
        self.message = message
        self.links = links or {}

    def to_dict(self) -> Dict:
        """Convert response to dictionary format."""
        response = {
            "status": "success" if self.status_code < 400 else "error",
            "metadata": self.metadata.to_dict(),
            "data": self.data
        }
        
        if self.message:
            response["message"] = self.message
            
        if self.links:
            response["links"] = self.links
            
        return response

class ResponseFormatterMiddleware(BaseHTTPMiddleware):
    """Middleware for formatting API responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Process and format response.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Formatted JSON response
        """
        request_id = str(uuid.uuid4())
        path = request.url.path
        start_time = time.time()
        
        # Store request ID for logging/tracking
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Skip formatting for non-JSON responses
            if not response.headers.get("content-type", "").startswith("application/json"):
                return response
                
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Create metadata
            metadata = ResponseMetadata(
                request_id=request_id,
                path=path,
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=duration_ms
            )
            
            # Get response data
            body = await self._get_response_body(response)
            
            # Format response
            formatted = FormattedResponse(
                data=body,
                metadata=metadata,
                status_code=response.status_code,
                message=self._get_status_message(response.status_code),
                links=self._get_response_links(request, body)
            )
            
            # Track response time
            track_response_time(
                path=path,
                status=response.status_code,
                duration_ms=duration_ms
            )
            
            return JSONResponse(
                status_code=response.status_code,
                content=formatted.to_dict(),
                headers=response.headers
            )
            
        except Exception as e:
            logger.error(f"Response formatting failed: {str(e)}")
            # Return original response on formatting error
            return response
    
    async def _get_response_body(self, response) -> Any:
        """Extract response body content.
        
        Args:
            response: FastAPI response
            
        Returns:
            Response body content
        """
        try:
            if hasattr(response, "body"):
                return await response.json()
            return {}
        except:
            return {}
    
    def _get_status_message(self, status_code: int) -> Optional[str]:
        """Get standard message for status code.
        
        Args:
            status_code: HTTP status code
            
        Returns:
            Standard message string
        """
        messages = {
            200: "Request successful",
            201: "Resource created successfully",
            400: "Invalid request parameters",
            401: "Authentication required",
            403: "Permission denied",
            404: "Resource not found",
            429: "Too many requests",
            500: "Internal server error"
        }
        return messages.get(status_code)
    
    def _get_response_links(self, request: Request, data: Any) -> Dict:
        """Generate HATEOAS links for response.
        
        Args:
            request: FastAPI request
            data: Response data
            
        Returns:
            Dictionary of related links
        """
        links = {}
        base_url = str(request.base_url).rstrip("/")
        path = request.url.path
        
        # Add links based on endpoint and response data
        if path == "/validate/email":
            # Add link to get validation result
            if isinstance(data, dict) and "id" in data:
                links["result"] = f"{base_url}/results/{data['id']}"
                
        elif path == "/validate/batch":
            # Add link to get batch results
            if isinstance(data, dict) and "batch_id" in data:
                links["results"] = f"{base_url}/batch/{data['batch_id']}/results"
                
        return links