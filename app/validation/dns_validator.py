"""DNS validation implementation for email domains."""

import asyncio
import dns.asyncresolver
import dns.exception
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta

from app.config.settings import settings

class DNSValidationError(Exception):
    """Custom exception for DNS validation errors."""
    pass

class DNSCache:
    """Cache for DNS lookup results."""
    
    def __init__(self, ttl: int = 3600):
        self._cache: Dict[str, Tuple[datetime, List[str]]] = {}
        self.ttl = ttl
        
    def get(self, domain: str) -> Optional[List[str]]:
        """Get cached DNS records if they exist and haven't expired."""
        if domain in self._cache:
            timestamp, records = self._cache[domain]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return records
            del self._cache[domain]
        return None
        
    def set(self, domain: str, records: List[str]) -> None:
        """Cache DNS records for a domain."""
        self._cache[domain] = (datetime.now(), records)
        
    def clear(self) -> None:
        """Clear all cached records."""
        self._cache.clear()

class DNSValidator:
    """DNS validator for email domains."""
    
    def __init__(self):
        self.resolver = dns.asyncresolver.Resolver()
        self.resolver.timeout = settings.DNS_TIMEOUT
        self.resolver.lifetime = settings.DNS_LIFETIME
        self.cache = DNSCache(ttl=settings.DNS_CACHE_TTL)
        
    async def validate_domain(self, domain: str) -> bool:
        """Validate a domain by checking its DNS records.
        
        Args:
            domain: The domain to validate
            
        Returns:
            bool: True if domain has valid DNS records
            
        Raises:
            DNSValidationError: If DNS lookup fails
        """
        try:
            # Check cache first
            cached_records = self.cache.get(domain)
            if cached_records is not None:
                return bool(cached_records)
                
            # Query A records
            try:
                a_records = await self.resolver.resolve(domain, 'A')
                if a_records:
                    self.cache.set(domain, [str(r) for r in a_records])
                    return True
            except dns.exception.DNSException:
                # No A records, try MX records
                pass
                
            # Query MX records
            try:
                mx_records = await self.resolver.resolve(domain, 'MX')
                if mx_records:
                    self.cache.set(domain, [str(r.exchange) for r in mx_records])
                    return True
            except dns.exception.DNSException:
                return False
                
        except dns.exception.DNSException as e:
            raise DNSValidationError(f"DNS lookup failed: {str(e)}")
            
        return False
        
    async def get_mx_records(self, domain: str) -> List[str]:
        """Get MX records for a domain.
        
        Args:
            domain: The domain to lookup
            
        Returns:
            List[str]: List of MX records
            
        Raises:
            DNSValidationError: If DNS lookup fails
        """
        try:
            # Check cache first
            cached_records = self.cache.get(domain)
            if cached_records is not None:
                return cached_records
                
            # Query MX records
            mx_records = await self.resolver.resolve(domain, 'MX')
            records = [str(r.exchange) for r in mx_records]
            
            # Cache results
            self.cache.set(domain, records)
            
            return records
        except dns.exception.DNSException as e:
            raise DNSValidationError(f"MX lookup failed: {str(e)}")

# Global DNS validator instance
dns_validator = DNSValidator()