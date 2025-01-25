"""API request and response models.

This module defines Pydantic models for API request/response validation and documentation.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field

class ValidationRequest(BaseModel):
    """Single email validation request."""
    email: EmailStr = Field(..., description="Email address to validate")
    options: Optional[Dict] = Field(
        default={},
        description="Optional validation options"
    )

class BatchValidationRequest(BaseModel):
    """Batch email validation request."""
    emails: List[EmailStr] = Field(
        ...,
        description="List of email addresses to validate",
        max_items=100
    )
    options: Optional[Dict] = Field(
        default={},
        description="Optional validation options"
    )

class ValidationResponse(BaseModel):
    """Email validation response."""
    id: str = Field(..., description="Unique validation ID")
    email: EmailStr = Field(..., description="Validated email address")
    valid: bool = Field(..., description="Overall validity assessment")
    score: float = Field(
        ...,
        description="Risk score (0-100, higher = riskier)",
        ge=0,
        le=100
    )
    risk_level: str = Field(
        ...,
        description="Risk assessment level",
        regex='^(low|medium|high)$'
    )
    checks: Dict = Field(
        ...,
        description="Detailed validation check results"
    )
    created_at: str = Field(
        ...,
        description="Timestamp of validation"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if validation failed"
    )

class BatchValidationResponse(BaseModel):
    """Batch validation response."""
    batch_id: str = Field(..., description="Unique batch validation ID")
    results: List[ValidationResponse] = Field(
        ...,
        description="List of validation results"
    )
    summary: Dict = Field(
        ...,
        description="Batch validation summary stats"
    )
    created_at: str = Field(
        ...,
        description="Timestamp of validation"
    )

class ErrorResponse(BaseModel):
    """API error response."""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict] = Field(
        None,
        description="Additional error details"
    )