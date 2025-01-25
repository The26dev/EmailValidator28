"""
DNS Resolver Module
Performs DNS lookups and retrieves MX records.
Supports international domains and comprehensive DNS checks.
"""

import dns.resolver
import dns.exception
import idna
from typing import List, Dict, Optional, Tuple
from app.utils.exceptions import ValidationError
from app.utils.logger import setup_logger
from app.utils.cache_manager import CacheManager

logger = setup_logger('DNSResolver')

class DNSResolver:
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """Initialize DNS resolver with optional cache manager."""
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 3
        self.resolver.lifetime = 5
        self.cache = cache_manager

    def _get_cache_key(self, domain: str, record_type: str) -> str:
        """Generate cache key for DNS queries."""
        return f"dns:{domain}:{record_type}"

    def encode_idn(self, domain: str) -> str:
        """Encode an International Domain Name (IDN) to ASCII/punycode form."""
        try:
            return idna.encode(domain).decode('ascii')
        except idna.IDNAError as e:
            logger.error(f"IDN encoding error for domain {domain}: {e}")
            raise ValidationError(f"Invalid international domain name: {e}")

    def resolve_domain(self, domain: str) -> Dict[str, bool]:
        """Perform comprehensive domain resolution including A, AAAA, and NS records."""
        cache_key = self._get_cache_key(domain, "resolve")
        if self.cache:
            cached_result = self.cache.get_cache(cache_key)
            if cached_result:
                return cached_result

        encoded_domain = self.encode_idn(domain)
        results = {
            'a_record': False,
            'aaaa_record': False,
            'ns_record': False,
            'any_record': False
        }
        
        try:
            # Check A records (IPv4)
            try:
                self.resolver.resolve(encoded_domain, 'A')
                results['a_record'] = True
                results['any_record'] = True
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                pass

            # Check AAAA records (IPv6)
            try:
                self.resolver.resolve(encoded_domain, 'AAAA')
                results['aaaa_record'] = True
                results['any_record'] = True
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                pass

            # Check NS records
            try:
                self.resolver.resolve(encoded_domain, 'NS')
                results['ns_record'] = True
                results['any_record'] = True
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                pass

            if self.cache:
                self.cache.set_cache(cache_key, results, expire=3600)
            return results

        except dns.exception.Timeout:
            logger.error(f"DNS resolution timeout for domain {domain}")
            raise ValidationError("DNS resolution timeout")
        except Exception as e:
            logger.error(f"DNS resolution error for domain {domain}: {e}")
            raise ValidationError(f"DNS resolution failed: {str(e)}")

    def get_mx_records(self, domain: str) -> List[Tuple[int, str]]:
        """Retrieve and validate MX records for the domain."""
        cache_key = self._get_cache_key(domain, "mx")
        if self.cache:
            cached_result = self.cache.get_cache(cache_key)
            if cached_result:
                return cached_result

        encoded_domain = self.encode_idn(domain)
        try:
            mx_records = self.resolver.resolve(encoded_domain, 'MX')
            records = []
            
            for rdata in mx_records:
                priority = rdata.preference
                server = str(rdata.exchange).rstrip('.')
                records.append((priority, server))
            
            # Sort by priority
            records.sort(key=lambda x: x[0])
            
            if self.cache:
                self.cache.set_cache(cache_key, records, expire=3600)
            return records

        except dns.resolver.NXDOMAIN:
            logger.warning(f"No MX records found for domain {domain}")
            return []
        except dns.resolver.NoAnswer:
            logger.warning(f"No MX records found for domain {domain}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving MX records for {domain}: {e}")
            raise ValidationError(f"MX record lookup failed: {str(e)}")

    def verify_ptr_record(self, domain: str) -> Optional[str]:
        """Check for PTR records (reverse DNS)."""
        cache_key = self._get_cache_key(domain, "ptr")
        if self.cache:
            cached_result = self.cache.get_cache(cache_key)
            if cached_result:
                return cached_result

        try:
            # First get the A record
            a_records = self.resolver.resolve(self.encode_idn(domain), 'A')
            if not a_records:
                return None
                
            # Get the first IP
            ip = a_records[0].to_text()
            
            # Reverse the IP and append .in-addr.arpa.
            reverse_ip = '.'.join(reversed(ip.split('.'))) + '.in-addr.arpa'
            
            # Look up PTR record
            ptr_records = self.resolver.resolve(reverse_ip, 'PTR')
            if ptr_records:
                result = ptr_records[0].to_text().rstrip('.')
                if self.cache:
                    self.cache.set_cache(cache_key, result, expire=3600)
                return result
            return None
            
        except Exception as e:
            logger.debug(f"PTR record lookup failed for {domain}: {e}")
            return None