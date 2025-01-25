"""API route handlers for email validation endpoints."""
import logging
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import APIKeyHeader

from .models import (
    ValidationRequest,
    BatchValidationRequest,
    ValidationResponse,
    BatchValidationResponse,
    ErrorResponse
)
from ..utils.authentication import verify_api_key
from ..tasks import validate_email_task
from ..utils.rate_limiter import check_rate_limit
from ..utils.validation_orchestrator import validate_email, validate_emails_batch
from ..utils.results_handler import handler as results_handler

logger = logging.getLogger(__name__)

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key")

@router.post(
    "/validate/email",
    response_model=ValidationResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def validate_single_email(
    request: ValidationRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(api_key_header)
):
    """Validate a single email address."""
    try:
        # Verify API key
        user = verify_api_key(api_key)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )

        # Check rate limits
        if not check_rate_limit(user.id):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )

        # Validate email
        result = validate_email(request.email)

        # Schedule async tasks (result storage, notifications, etc)
        background_tasks.add_task(
            validate_email_task,
            email=request.email,
            save=True
        )

        return ValidationResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email validation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )

@router.post(
    "/validate/batch",
    response_model=BatchValidationResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def validate_email_batch(
    request: BatchValidationRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(api_key_header)
):
    """Validate multiple email addresses in batch."""
    try:
        # Verify API key
        user = verify_api_key(api_key)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )

        # Check rate limits
        if not check_rate_limit(user.id, len(request.emails)):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )

        # Validate emails in batch
        results = await validate_emails_batch(
            request.emails,
            batch_size=min(len(request.emails), 50)
        )

        # Calculate batch summary
        valid_count = sum(1 for r in results if r.get('valid', False))
        summary = {
            "total": len(results),
            "valid": valid_count,
            "invalid": len(results) - valid_count
        }

        # Schedule async tasks
        background_tasks.add_task(
            store_batch_results,
            results=results,
            user_id=user.id
        )

        return BatchValidationResponse(
            batch_id=str(uuid.uuid4()),
            results=results,
            summary=summary,
            created_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch validation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch validation failed: {str(e)}"
        )

@router.get(
    "/results/{validation_id}",
    response_model=ValidationResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_validation_result(
    validation_id: str,
    api_key: str = Depends(api_key_header)
):
    """Retrieve a validation result by ID."""
    try:
        # Verify API key
        user = verify_api_key(api_key)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )

        # Get cached result
        result = results_handler.get_cached_results(validation_id=validation_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Result not found: {validation_id}"
            )

        return ValidationResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve result: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve result: {str(e)}"
        )