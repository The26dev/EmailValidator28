"""Domain reputation checking module.

This module evaluates email domain trustworthiness using multiple factors including:
- Domain age and registration info
- Presence on blacklists/spam lists
- Historical spam complaints
- SSL/TLS support
- Web presence metrics
"""
import logging
import socket
import ssl
import whois
import requests
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .metrics import ValidationTimer
from .exceptions import DomainReputationError

logger = logging.getLogger(__name__)

# Reputation scoring weights
WEIGHTS = {
    "domain_age": 0.25,
    "blacklist_status": 0.30,
    "ssl_status": 0.15,
    "web_presence": 0.15,
    "mail_config": 0.15
}

# Well-known blacklist providers
BLACKLIST_SERVERS = [
    "zen.spamhaus.org",
    "bl.spamcop.net",
    "dnsbl.sorbs.net",
    "spam.abuse.ch",
    "cbl.abuseat.org"
]

@dataclass
class DomainReputation:
    """Domain reputation check results."""
    score: float
    risk_level: str
    details: Dict = None
    error: str = ""

class DomainReputationChecker:
    """Evaluates domain reputation using multiple factors."""

    def __init__(self):
        """Initialize checker with default thresholds."""
        self.high_risk_threshold = 70
        self.medium_risk_threshold = 40

    def check_reputation(self, domain: str) -> Dict:
        """Check domain reputation using multiple factors.
        
        Args:
            domain: Domain to evaluate
            
        Returns:
            Dict containing reputation results with fields:
                - score: Reputation score (0-100, higher = worse)
                - risk_level: Risk assessment (low/medium/high)
                - details: Detailed check results
                - error: Error message if check failed
        """
        with ValidationTimer():
            try:
                # Get domain age and registration info
                age_score = self._check_domain_age(domain)
                
                # Check domain against blacklists
                blacklist_score = self._check_blacklists(domain)
                
                # Check SSL/TLS configuration
                ssl_score = self._check_ssl(domain)
                
                # Check web presence
                web_score = self._check_web_presence(domain)
                
                # Check mail server configuration
                mail_score = self._check_mail_config(domain)
                
                # Calculate weighted reputation score
                total_score = sum([
                    age_score * WEIGHTS["domain_age"],
                    blacklist_score * WEIGHTS["blacklist_status"],
                    ssl_score * WEIGHTS["ssl_status"],
                    web_score * WEIGHTS["web_presence"],
                    mail_score * WEIGHTS["mail_config"]
                ])
                
                # Determine risk level
                if total_score >= self.high_risk_threshold:
                    risk_level = "high"
                elif total_score >= self.medium_risk_threshold:
                    risk_level = "medium"
                else:
                    risk_level = "low"
                    
                return DomainReputation(
                    score=total_score,
                    risk_level=risk_level,
                    details={
                        "domain_age_score": age_score,
                        "blacklist_score": blacklist_score,
                        "ssl_score": ssl_score,
                        "web_presence_score": web_score,
                        "mail_config_score": mail_score,
                        "factors": {
                            "domain_age": self._domain_age_details,
                            "blacklists": self._blacklist_details,
                            "ssl": self._ssl_details,
                            "web": self._web_details,
                            "mail": self._mail_details
                        }
                    }
                ).__dict__
                
            except Exception as e:
                logger.error(f"Domain reputation check failed: {str(e)}")
                return DomainReputation(
                    score=100,  # Assume worst score on failure
                    risk_level="high",
                    error=str(e)
                ).__dict__

    def _check_domain_age(self, domain: str) -> float:
        """Check domain registration age."""
        try:
            w = whois.whois(domain)
            if w.creation_date:
                # Convert to datetime if needed
                if isinstance(w.creation_date, list):
                    creation_date = w.creation_date[0]
                else:
                    creation_date = w.creation_date
                
                age_days = (datetime.now() - creation_date).days
                self._domain_age_details = {
                    "age_days": age_days,
                    "creation_date": creation_date.isoformat(),
                    "registrar": w.registrar
                }
                
                # Score inversely proportional to age, max age considered is 5 years
                max_age = 5 * 365  # 5 years in days
                return max(0, min(100, (max_age - age_days) / max_age * 100))
                
        except Exception as e:
            logger.warning(f"Domain age check failed: {str(e)}")
            self._domain_age_details = {"error": str(e)}
            return 50  # Neutral score on failure
            
    def _check_blacklists(self, domain: str) -> float:
        """Check domain presence on blacklists."""
        listed_on = []
        
        def check_single_blacklist(bl_server):
            try:
                query = f"{domain}."
                resolver = socket.gethostbyname_ex(bl_server)
                if resolver:
                    return bl_server
            except:
                pass
            return None
            
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_bl = {
                executor.submit(check_single_blacklist, bl): bl 
                for bl in BLACKLIST_SERVERS
            }
            
            for future in as_completed(future_to_bl):
                if future.result():
                    listed_on.append(future.result())
                    
        self._blacklist_details = {
            "checked": BLACKLIST_SERVERS,
            "listed_on": listed_on,
            "total_listings": len(listed_on)
        }
        
        # Score based on number of blacklist appearances
        return len(listed_on) / len(BLACKLIST_SERVERS) * 100
            
    def _check_ssl(self, domain: str) -> float:
        """Check domain SSL/TLS configuration."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
            self._ssl_details = {
                "has_ssl": True,
                "issuer": cert["issuer"],
                "valid_until": cert["notAfter"]
            }
            return 0  # Good SSL = low risk
            
        except Exception as e:
            logger.warning(f"SSL check failed: {str(e)}")
            self._ssl_details = {
                "has_ssl": False,
                "error": str(e)
            }
            return 100  # No/bad SSL = high risk
            
    def _check_web_presence(self, domain: str) -> float:
        """Check domain web presence."""
        try:
            response = requests.get(f"https://{domain}", timeout=5)
            
            self._web_details = {
                "status_code": response.status_code,
                "has_website": response.status_code == 200
            }
            
            return 0 if response.status_code == 200 else 50
            
        except Exception as e:
            logger.warning(f"Web presence check failed: {str(e)}")
            self._web_details = {
                "error": str(e),
                "has_website": False
            }
            return 50  # Neutral score on failure
            
    def _check_mail_config(self, domain: str) -> float:
        """Check mail server configuration."""
        try:
            # Check MX records
            mx_records = socket.getaddrinfo(f"@{domain}", None)
            
            # Check SPF record
            try:
                socket.gethostbyname(f"_spf.{domain}")
                has_spf = True
            except:
                has_spf = False
                
            # Check DMARC record
            try:
                socket.gethostbyname(f"_dmarc.{domain}")
                has_dmarc = True
            except:
                has_dmarc = False
                
            self._mail_details = {
                "has_mx": bool(mx_records),
                "has_spf": has_spf,
                "has_dmarc": has_dmarc
            }
            
            # Score based on presence of records
            score = 0
            if not mx_records:
                score += 40
            if not has_spf:
                score += 30
            if not has_dmarc:
                score += 30
                
            return score
            
        except Exception as e:
            logger.warning(f"Mail config check failed: {str(e)}")
            self._mail_details = {"error": str(e)}
            return 50  # Neutral score on failure

# Global checker instance
checker = DomainReputationChecker()