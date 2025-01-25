"""Risk score calculation utilities."""
from typing import Dict

def calculate_risk_score(validation_result: Dict) -> int:
    """Calculate risk score from validation results.
    
    Args:
        validation_result: Complete validation results dictionary
        
    Returns:
        int: Risk score from 0-100 (higher is better)
    """
    score = 0
    weights = {
        "syntax": 20,
        "dns": 30,
        "smtp": 20,
        "disposable": 10,
        "spam_trap": 10,
        "reputation": 10
    }
    
    # Basic checks
    if validation_result["checks"]["syntax"]["is_valid"]:
        score += weights["syntax"]
        
    # DNS checks 
    dns_score = 0
    if validation_result["checks"]["dns"].get("has_mx"):
        dns_score += 15
    if validation_result["checks"]["dns"].get("has_a"):
        dns_score += 10
    if validation_result["checks"]["dns"].get("has_ptr"):
        dns_score += 5
    score += min(dns_score, weights["dns"])
    
    # SMTP check
    if validation_result["checks"].get("smtp", {}).get("verified"):
        score += weights["smtp"]
        
    # Disposable check (negative)
    if not validation_result["checks"]["disposable"]["is_disposable"]:
        score += weights["disposable"]
        
    # Spam trap check (negative)  
    if not validation_result["checks"]["spam_trap"]["is_trap"]:
        score += weights["spam_trap"]
        
    # Domain reputation
    reputation_score = validation_result["checks"]["reputation"].get("score", 0)
    score += int((weights["reputation"] * reputation_score) / 100)
    
    return min(max(score, 0), 100)