"""Job schemas for API requests and responses."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class JobBase(BaseModel):
    """Base job schema."""

    title: str = Field(..., description="Job title")
    company: str | None = Field(None, description="Company name")
    description_text: str = Field(..., description="Job description text")


class JobCreate(JobBase):
    """Schema for creating a job."""

    source: str = Field(default="paste", description="Source of job description")


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
