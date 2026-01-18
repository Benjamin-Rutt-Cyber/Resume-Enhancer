"""Job schemas for API requests and responses.

SECURITY: Input validation with max_length constraints to prevent abuse.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

# SECURITY: Maximum lengths for input validation
MAX_JOB_TITLE_LENGTH = 200
MAX_COMPANY_LENGTH = 200
MAX_JOB_DESCRIPTION_LENGTH = 20000  # 20k chars as per spec


class JobBase(BaseModel):
    """Base job schema."""

    title: str = Field(
        ...,
        description="Job title",
        min_length=1,
        max_length=MAX_JOB_TITLE_LENGTH
    )
    company: str | None = Field(
        None,
        description="Company name",
        max_length=MAX_COMPANY_LENGTH
    )
    description_text: str = Field(
        ...,
        description="Job description text",
        min_length=50,  # Minimum for meaningful job descriptions
        max_length=MAX_JOB_DESCRIPTION_LENGTH
    )


class JobCreate(JobBase):
    """Schema for creating a job."""

    source: str = Field(
        default="paste",
        description="Source of job description",
        max_length=50
    )


class JobResponse(JobBase):
    """Schema for job response."""

    id: UUID
    file_path: str
    source: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Schema for list of jobs."""

    jobs: list[JobResponse]
    total: int
