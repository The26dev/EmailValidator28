"""Batch email validation utilities."""
import asyncio
import logging
from typing import Dict, List

from app.utils.exceptions import ValidationError
from app.utils.validation_orchestrator import validate_email

logger = logging.getLogger(__name__)

async def validate_emails_batch(emails: List[str], batch_size: int = 50) -> List[Dict]:
    """Validate multiple email addresses in parallel batches.
    
    Args:
        emails: List of email addresses to validate
        batch_size: Number of concurrent validations
        
    Returns:
        List of validation results in same order as input emails
    """
    try:
        # Process emails in batches
        results = []
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            batch_results = await asyncio.gather(
                *(validate_email(email) for email in batch),
                return_exceptions=True
            )
            
            # Handle any exceptions in batch results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Validation failed for {batch[j]}: {str(result)}")
                    results.append({
                        "email": batch[j],
                        "is_valid": False,
                        "error": str(result),
                        "checks": {},
                        "score": 0
                    })
                else:
                    results.append(result)
                    
        return results
        
    except Exception as e:
        logger.error(f"Batch validation failed: {str(e)}")
        raise ValidationError(f"Batch validation failed: {str(e)}")