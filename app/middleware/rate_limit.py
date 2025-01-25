"""Rate limiting middleware implementation."""

from datetime import datetime, timedelta
from typing import Dict, Tuple
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, rate_limit: int = 100, time_window: int = 60):
        """Initialize rate limiter.
        
        Args:
            rate_limit: Maximum number of requests allowed in time window
            time_window: Time window in seconds
        """
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.requests: Dict[str, Tuple[int, datetime]] = {}
        
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Check if client has previous requests
        if client_ip in self.requests:
            count, start_time = self.requests[client_ip]
            
            # Reset if time window has passed
            if datetime.now() - start_time > timedelta(seconds=self.time_window):
                self.requests[client_ip] = (1, datetime.now())
            else:
                # Increment count
                count += 1
                if count > self.rate_limit:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many requests"}
                    )
                self.requests[client_ip] = (count, start_time)
        else:
            # First request from this client
            self.requests[client_ip] = (1, datetime.now())
            
        return await call_next(request)