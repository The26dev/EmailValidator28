"""Email DNS validation implementation."""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from .dns_resolver import DNSResolver
from .cache_manager import CacheManager
from .logger import get_logger
from .exceptions import (
    DNSLookupError,
    DNSValidationError,
    RateLimitExceeded,
    ValidationError,
)

logger = get_logger(__name__)

class EmailDNSValidator:
    """Handles DNS-related email validation tasks with caching and rate limiting."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.dns_resolver = DNSResolver(cache_manager)
        self.cache_manager = cache_manager
        self.last_check = {}  # Rate limiting tracker

    def _get_cache_key(self, domain: str) -> str:
        """Generate cache key for domain validation results."""
        return f"dns_validation:{domain}"

    def _check_rate_limit(self, domain: str, limit: int = 10, window: int = 60) -> bool:
        """Check if domain has exceeded rate limit.
        
        Args:
            domain: Domain to check
            limit: Maximum checks per window
            window: Time window in seconds
        
        Returns:
            bool: True if rate limit is exceeded
        """
        now = datetime.utcnow()
        if domain in self.last_check:
            checks = self.last_check[domain]
            # Remove old checks
            checks = [t for t in checks if now - t < timedelta(seconds=window)]
            if len(checks) >= limit:
                return True
            self.last_check[domain] = checks + [now]
        else:
            self.last_check[domain] = [now]
        return False

    async def validate_domain(self, domain: str) -> Dict[str, bool]:
        """Validate email domain through DNS checks.
        
        Performs:
        - MX record validation
        - A/AAAA record fallback
        - PTR record verification
        - Disposable email detection
        
        Args:
            domain: Email domain to validate
            
        Returns:
            Dict containing validation results
            
        Raises:
            DNSValidationError: If domain fails validation
            RateLimitExceeded: If domain exceeds rate limit
        """
        try:
            # Check rate limit
            if self._check_rate_limit(domain):
                raise RateLimitExceeded(f"Rate limit exceeded for domain: {domain}")

            # Check cache first
            cache_key = self._get_cache_key(domain)
            if self.cache_manager:
                cached = await self.cache_manager.get(cache_key)
                if cached:
                    return cached

            # Perform DNS validation
            result = await self.dns_resolver.resolve_domain(domain)
            
            # Get MX records
            mx_records = await self.dns_resolver.get_mx_records(domain)
            result["has_mx"] = bool(mx_records)
            
            # Verify PTR record
            ptr_record = await self.dns_resolver.verify_ptr_record(domain)
            result["has_ptr"] = bool(ptr_record)
            
            # Cache results
            if self.cache_manager:
                await self.cache_manager.set(cache_key, result, ttl=3600)  # 1 hour cache
                
            return result

        except DNSLookupError as e:
            logger.warning(f"DNS lookup failed for domain {domain}: {str(e)}")
            raise DNSValidationError(f"DNS validation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error validating domain {domain}: {str(e)}")
            raise ValidationError(f"Domain validation failed: {str(e)}")

    async def validate_domains_batch(
        self, domains: List[str], batch_size: int = 50
    ) -> List[Dict[str, bool]]:
        """Validate multiple domains in parallel batches.
        
        Args:
            domains: List of domains to validate
            batch_size: Number of concurrent validations
            
        Returns:
            List of validation results
        """
        try:
            # Split domains into batches
            results = []
            for i in range(0, len(domains), batch_size):
                batch = domains[i:i + batch_size]
                batch_results = await asyncio.gather(
                    *[self.validate_domain(domain) for domain in batch],
                    return_exceptions=True
                )
                results.extend(batch_results)
            return results

        except Exception as e:
            logger.error(f"Batch validation failed: {str(e)}")
            raise ValidationError(f"Batch validation failed: {str(e)}")

    def get_validation_score(self, result: Dict[str, bool]) -> int:
        """Calculate domain validation score based on DNS checks.
        
        Args:
            result: DNS validation results
            
        Returns:
            int: Score from 0-100
        """
        score = 0
        weights = {
            "has_mx": 40,
            "has_a": 20,
            "has_aaaa": 10,
            "has_ptr": 30
        }
        
        for check, weight in weights.items():
            if result.get(check, False):
                score += weight
                
        return score