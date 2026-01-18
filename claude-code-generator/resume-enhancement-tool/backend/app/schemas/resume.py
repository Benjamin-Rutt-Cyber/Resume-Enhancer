"""Resume schemas for API requests and responses.

SECURITY: Input validation with max_length constraints.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

# SECURITY: Maximum lengths for input validation
MAX_FILENAME_LENGTH = 255
MAX_FORMAT_LENGTH = 10
MAX_RESUME_TEXT_LENGTH = 50000  # 50k chars as per spec


class ResumeBase(BaseModel):
    """Base resume schema."""

    filename: str = Field(
        ...,
        description="Original filename",
        min_length=1,
        max_length=MAX_FILENAME_LENGTH
    )
    original_format: str = Field(
        ...,
        description="File format (pdf, docx)",
        max_length=MAX_FORMAT_LENGTH
    )


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
