"""Resume schemas for API requests and responses."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ResumeBase(BaseModel):
    """Base resume schema."""

    filename: str = Field(..., description="Original filename")
    original_format: str = Field(..., description="File format (pdf, docx)")


class ResumeCreate(ResumeBase):
    """Schema for creating a resume."""

    pass


class ResumeResponse(ResumeBase):
    """Schema for resume response."""

    id: UUID
    file_path: str
    extracted_text_path: str
    upload_date: datetime
    file_size_bytes: int
    word_count: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    """Schema for list of resumes."""

    resumes: list[ResumeResponse]
    total: int
