"""Schemas for comparison view."""

from pydantic import BaseModel


class ComparisonResponse(BaseModel):
    """Response for side-by-side comparison view."""

    enhancement_id: str
    original_text: str
    enhanced_text: str
    enhancement_type: str
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "enhancement_id": "123e4567-e89b-12d3-a456-426614174000",
                "original_text": "John Doe\n\nSoftware Engineer with 5 years experience...",
                "enhanced_text": "# John Doe\n\n**Software Engineer | 5+ Years Experience**\n\n...",
                "enhancement_type": "job_tailoring",
                "status": "completed"
            }
        }
