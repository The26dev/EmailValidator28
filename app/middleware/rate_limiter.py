"""Rate limiting middleware.

Provides distributed rate limiting using Redis as a backend store.
Supports different rate limit tiers and flexible time windows.
"""
import time
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.cache_manager import cache
from ..utils.metrics import track_rate_limit

logger = logging.getLogger(__name__)

@dataclass
class RateLimitTier:
    """Rate limit configuration for an API tier."""
    requests_per_second: int
    requests_per_minute: int
    requests_per_hour: int
    burst_size: int = 0
    tier_name: str = "default"

# Rate limit tiers
RATE_LIMIT_TIERS = {
    "free": RateLimitTier(
        requests_per_second=2,
        requests_per_minute=30,
        requests_per_hour=500,
        burst_size=5,
        tier_name="free"
    ),
    "basic": RateLimitTier(
        requests_per_second=5,
        requests_per_minute=100,
        requests_per_hour=2000,
        burst_size=10,
        tier_name="basic"
    ),
    "premium": RateLimitTier(
        requests_per_second=10,
        requests_per_minute=300,
        requests_per_hour=5000,
        burst_size=20,
        tier_name="premium"
    ),
    "enterprise": RateLimitTier(
        requests_per_second=50,
        requests_per_minute=1000,
        requests_per_hour=20000,
        burst_size=100,
        tier_name="enterprise"
    )
}

class RateLimitError(HTTPException):
    """Custom exception for rate limit errors."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=429,
            detail=detail,
            headers={"Retry-After": "60"}
        )

from .sqlite_rate_limiter import SQLiteRateLimiter
from ..config.sqlite_config import RATE_LIMIT_DB_PATH

class RateLimiter(SQLiteRateLimiter):
    """Rate limiter implementation using SQLite."""
    
    def __init__(self, cache_prefix: str = "ratelimit"):
        # Initialize with SQLite backend
        super().__init__(db_path=RATE_LIMIT_DB_PATH, cache_prefix=cache_prefix)
        """Initialize rate limiter.
        
        Args:
            cache_prefix: Prefix for Redis cache keys
        """
        self.prefix = cache_prefix
        
    def _get_window_key(self, key: str, window: str) -> str:
        """Get Redis key for a rate limit window."""
        return f"{self.prefix}:{key}:{window}"
        
    def check_rate_limit(
        self,
        key: str,
        tier: str = "free"
    ) -> Tuple[bool, Dict]:
        """Check if request is within rate limits.
        
        Args:
            key: Unique key to track (usually API key or IP)
            tier: Rate limit tier to apply
            
        Returns:
            Tuple of (allowed, limit_info)
        """
        now = int(time.time())
        pipe = cache.redis.pipeline()

        # Get rate limit config
        limits = RATE_LIMIT_TIERS.get(tier, RATE_LIMIT_TIERS["free"])
        
        # Check each time window
        windows = {
            "second": (now, limits.requests_per_second),
            "minute": (now // 60, limits.requests_per_minute),
            "hour": (now // 3600, limits.requests_per_hour)
        }
        
        # Pipeline Redis commands
        for window, (timestamp, limit) in windows.items():
            window_key = self._get_window_key(key, window)
            pipe.get(window_key)
            pipe.ttl(window_key)
            
        results = pipe.execute()
        allowed = True
        info = {}
        
        # Process results
        for i, window in enumerate(windows.keys()):
            count = int(results[i*2] or 0)
            ttl = results[i*2 + 1]
            limit = windows[window][1]
            
            if count >= limit:
                allowed = False
            
            info[window] = {
                "remaining": max(0, limit - count),
                "limit": limit,
                "reset": ttl if ttl > 0 else 60,
                "current": count
            }
            
        return allowed, info
        
    def increment(
        self,
        key: str,
        tier: str = "free",
        cost: int = 1
    ) -> None:
        """Increment counters for rate limit windows.
        
        Args:
            key: Unique key to track
            tier: Rate limit tier
            cost: Cost of this request
        """
        now = int(time.time())
        pipe = cache.redis.pipeline()
        
        # Increment each window
        windows = {
            "second": (1, now),
            "minute": (60, now // 60),
            "hour": (3600, now // 3600)
        }
        
        for window, (expiry, timestamp) in windows.items():
            window_key = self._get_window_key(key, window)
            pipe.incr(window_key, cost)
            pipe.expire(window_key, expiry)
            
        pipe.execute()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    def __init__(self, app):
        super().__init__(app)
        self.limiter = RateLimiter()
        
    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiter.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response
            
        Raises:
            RateLimitError if rate limit exceeded
        """
        # Get API key from header
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            # No API key means use IP-based limiting
            key = request.client.host
            tier = "free"
        else:
            # Use API key-based limiting with user's tier
            key = api_key
            # TODO: Get user's actual tier from DB
            tier = "basic"
            
        # Check rate limits
        allowed, info = self.limiter.check_rate_limit(key, tier)
        
        if not allowed:
            # Track rate limit event
            track_rate_limit(key, tier)
            
            # Return rate limit error
            window, data = next(
                ((w, d) for w, d in info.items() if d["remaining"] == 0),
                ("minute", info["minute"])
            )
            raise RateLimitError(
                f"Rate limit exceeded. Try again in {data['reset']} seconds."
            )
            
        try:
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            minute_info = info["minute"]
            response.headers.update({
                "X-RateLimit-Limit": str(minute_info["limit"]),
                "X-RateLimit-Remaining": str(minute_info["remaining"]),
                "X-RateLimit-Reset": str(minute_info["reset"])
            })
            
            # Increment counters
            self.limiter.increment(key, tier)
            
            return response
            
        except RateLimitError:
            raise
        except Exception as e:
            logger.error(f"Error in rate limit middleware: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )