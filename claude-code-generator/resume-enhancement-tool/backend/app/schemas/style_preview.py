"""Pydantic schemas for style preview operations."""

from typing import List
from pydantic import BaseModel, Field
from uuid import UUID


class StylePreviewItem(BaseModel):
    """Single style preview item."""

    style: str = Field(..., description="Style identifier (professional, executive, etc.)")
    name: str = Field(..., description="Display name of the style")
    description: str = Field(..., description="Description of the style")
    preview_text: str = Field(..., description="Generated preview text for this style")

    model_config = {
        "json_schema_extra": {
            "example": {
                "style": "professional",
                "name": "Professional",
                "description": "Traditional corporate tone with formal language",
                "preview_text": "Experienced software engineer with 5+ years of experience..."
            }
        }
    }


class StylePreviewsResponse(BaseModel):
    """Response containing all style previews."""

    resume_id: UUID = Field(..., description="Resume ID")
    previews: List[StylePreviewItem] = Field(..., description="List of style previews")

    model_config = {
        "json_schema_extra": {
            "example": {
                "resume_id": "123e4567-e89b-12d3-a456-426614174000",
                "previews": [
                    {
                        "style": "professional",
                        "name": "Professional",
                        "description": "Traditional corporate tone",
                        "preview_text": "Experienced software engineer..."
                    }
                ]
            }
        }
    }


class StyleSelectionRequest(BaseModel):
    """Request to save selected style."""

    style: str = Field(..., description="Selected style name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "style": "professional"
            }
        }
    }


class StyleSelectionResponse(BaseModel):
    """Response after saving style selection."""

    message: str = Field(..., description="Confirmation message")
    selected_style: str = Field(..., description="The selected style")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Style selected successfully",
                "selected_style": "professional"
            }
        }
    }


class StyleUpdateRequest(BaseModel):
    """Request to update resume writing style."""

    new_style: str = Field(
        ...,
        description="New writing style to apply",
        pattern="^(professional|executive|technical|creative|concise)$"
    )
    reason: str = Field(
        default="",
        description="Optional reason for the style change",
        max_length=500
    )
    source: str = Field(
        default="user",
        description="Source of the update (user or agent_recommendation)",
        pattern="^(user|agent_recommendation)$"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "new_style": "technical",
                "reason": "Job requires detailed technical expertise",
                "source": "agent_recommendation"
            }
        }
    }


class StyleUpdateResponse(BaseModel):
    """Response after updating resume style."""

    message: str = Field(..., description="Confirmation message")
    resume_id: UUID = Field(..., description="Resume ID")
    old_style: str = Field(..., description="Previous style")
    new_style: str = Field(..., description="Updated style")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Resume style updated successfully",
                "resume_id": "123e4567-e89b-12d3-a456-426614174000",
                "old_style": "professional",
                "new_style": "technical"
            }
        }
    }
