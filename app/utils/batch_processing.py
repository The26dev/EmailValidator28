"""Batch processing utilities for email validation."""
from typing import Dict, List
import asyncio
from app.utils.validation_orchestrator import validate_email

async def process_email_batch(batch: List[str]) -> List[Dict]:
    """
    Process a batch of emails concurrently.
    
    Args:
        batch: List of email addresses to validate.
        
    Returns:
        List of validation results.
    """
    tasks = []
    for email in batch:
        tasks.append(asyncio.create_task(validate_email(email)))
    
    batch_results = []
    completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
    
    for email, result in zip(batch, completed_tasks):
        if isinstance(result, Exception):
            error_result = {
                "email": email,
                "is_valid": False,
                "status": "Error",
                "error": str(result)
            }
            batch_results.append(error_result)
        else:
            batch_results.append(result)
    
    return batch_results

def generate_batch_summary(results: List[Dict]) -> Dict:
    """
    Generate summary statistics for batch validation results.
    
    Args:
        results: List of validation results.
        
    Returns:
        Dictionary containing summary statistics.
    """
    return {
        "total": len(results),
        "valid": sum(1 for r in results if r.get("is_valid", False)),
        "invalid": sum(1 for r in results if not r.get("is_valid", False)),
        "errors": sum(1 for r in results if r.get("status") == "Error")
    }