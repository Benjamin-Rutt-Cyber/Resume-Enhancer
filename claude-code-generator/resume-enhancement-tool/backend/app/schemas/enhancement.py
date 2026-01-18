"""Enhancement schemas for API requests and responses.

SECURITY: Input validation with strict field constraints.
"""

from datetime import datetime
from uuid import UUID
from typing import Literal
from pydantic import BaseModel, Field

# Valid enhancement types and industries
VALID_ENHANCEMENT_TYPES = ("job_tailoring", "industry_revamp")
VALID_INDUSTRIES = ("IT", "Cybersecurity", "Finance")


class EnhancementBase(BaseModel):
    """Base enhancement schema."""

    resume_id: UUID = Field(..., description="Resume ID to enhance")
    enhancement_type: Literal["job_tailoring", "industry_revamp"] = Field(
        ...,
        description="Type: job_tailoring or industry_revamp"
    )


class EnhancementTailorCreate(EnhancementBase):
    """Schema for creating a job tailoring enhancement."""

    job_id: UUID = Field(..., description="Job ID to tailor resume for")
    run_analysis: bool = Field(
        default=False,
        description="Whether to run ATS keyword analysis and job match scoring"
    )

    class Config:
        extra = "forbid"


class EnhancementRevampCreate(BaseModel):
    """Schema for creating an industry revamp enhancement."""

    resume_id: UUID = Field(..., description="Resume ID to enhance")
    industry: Literal["IT", "Cybersecurity", "Finance"] = Field(
        ...,
        description="Target industry (IT, Cybersecurity, Finance)"
    )

    class Config:
        extra = "forbid"


class EnhancementResponse(EnhancementBase):
    """Schema for enhancement response."""

    id: UUID
    job_id: UUID | None
    industry: str | None
    output_path: str | None
    pdf_path: str | None
    docx_path: str | None

    # Cover letter fields
    cover_letter_path: str | None
    cover_letter_pdf_path: str | None
    cover_letter_docx_path: str | None
    cover_letter_status: str
    cover_letter_error: str | None

    run_analysis: bool
    job_match_score: int | None
    status: str
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None
    updated_at: datetime

    class Config:
        from_attributes = True


class EnhancementListResponse(BaseModel):
    """Schema for list of enhancements."""

    enhancements: list[EnhancementResponse]
    total: int
