"""API routes for style preview operations."""

import logging
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...models.resume import Resume
from ...models.user import User
from ...schemas.style_preview import (
    StylePreviewsResponse,
    StylePreviewItem,
    StyleSelectionRequest,
    StyleSelectionResponse
)
from ...services.anthropic_service import AnthropicService
from ...config.styles import STYLES, validate_style
from ..dependencies import get_db, get_anthropic_service, get_current_active_user
from ...core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Workspace root
WORKSPACE_ROOT = Path("workspace")


@router.post("/resumes/{resume_id}/style-previews", response_model=StylePreviewsResponse, deprecated=True)
async def generate_style_previews(
    resume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    anthropic_service: AnthropicService = Depends(get_anthropic_service),
):
    """Generate style previews for a resume's professional summary.

    DEPRECATED: This endpoint has been disabled to eliminate API costs.
    The frontend now uses static style selection with predefined descriptions.
    Use the POST /resumes/{resume_id}/select-style endpoint to save style preferences.

    Args:
        resume_id: Resume UUID
        db: Database session
        anthropic_service: Anthropic API service

    Returns:
        StylePreviewsResponse with all 5 style previews

    Raises:
        HTTPException: Always returns 410 Gone (endpoint disabled)
    """
    logger.warning(
        f"Deprecated style preview API called for resume {resume_id}. "
        "This endpoint is disabled to reduce API costs. "
        "Frontend should use static style selection."
    )

    raise HTTPException(
        status_code=410,
        detail=(
            "AI style preview generation has been disabled to eliminate API costs. "
            "Please use the static style selection in the frontend. "
            "The frontend displays 5 predefined writing styles (Professional, Executive, "
            "Technical, Creative, Concise) with clear descriptions. "
            "Use POST /resumes/{id}/select-style to save your choice."
        )
    )


@router.get("/resumes/{resume_id}/style-previews", response_model=StylePreviewsResponse)
async def get_style_previews(
    resume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve existing style previews for a resume.

    Args:
        resume_id: Resume UUID
        db: Database session

    Returns:
        StylePreviewsResponse with all style previews

    Raises:
        HTTPException: If resume not found or previews not generated
    """
    # Get resume
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail=f"Resume not found: {resume_id}")

    # Verify ownership
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resume")

    # Check if previews have been generated
    if not resume.style_previews_generated:
        raise HTTPException(
            status_code=404,
            detail="Style previews not generated yet. Call POST /resumes/{id}/style-previews first."
        )

    # Read previews from workspace
    previews_dir = WORKSPACE_ROOT / "resumes" / "original" / str(resume_id) / "style_previews"

    if not previews_dir.exists():
        raise HTTPException(status_code=404, detail="Style previews directory not found")

    preview_items = []
    for style_name in STYLES.keys():
        preview_file = previews_dir / f"{style_name}.txt"
        if preview_file.exists():
            try:
                preview_text = preview_file.read_text(encoding="utf-8")
                preview_items.append(
                    StylePreviewItem(
                        style=style_name,
                        name=STYLES[style_name]["name"],
                        description=STYLES[style_name]["description"],
                        preview_text=preview_text
                    )
                )
            except Exception as e:
                logger.error(f"Error reading {style_name} preview: {str(e)}")

    if not preview_items:
        raise HTTPException(status_code=404, detail="No style preview files found")

    return StylePreviewsResponse(
        resume_id=resume_id,
        previews=preview_items
    )


@router.post("/resumes/{resume_id}/select-style", response_model=StyleSelectionResponse)
async def select_style(
    resume_id: UUID,
    style_selection: StyleSelectionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Save user's selected style for a resume.

    Args:
        resume_id: Resume UUID
        style_selection: Style selection request
        db: Database session

    Returns:
        StyleSelectionResponse with confirmation

    Raises:
        HTTPException: If resume not found or style invalid
    """
    # Get resume
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail=f"Resume not found: {resume_id}")

    # Verify ownership
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resume")

    # Validate style
    if not validate_style(style_selection.style):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid style: {style_selection.style}. Valid styles: {list(STYLES.keys())}"
        )

    # Save style selection
    resume.selected_style = style_selection.style
    db.commit()
    db.refresh(resume)

    logger.info(f"Style '{style_selection.style}' selected for resume {resume_id}")

    return StyleSelectionResponse(
        message="Style selected successfully",
        selected_style=resume.selected_style
    )
