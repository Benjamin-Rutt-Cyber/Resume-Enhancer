"""Comparison view API routes."""

import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Enhancement, Resume
from app.schemas.comparison import ComparisonResponse

logger = logging.getLogger(__name__)

router = APIRouter()
WORKSPACE_ROOT = Path("workspace")


@router.get("/enhancements/{enhancement_id}/comparison", response_model=ComparisonResponse)
async def get_comparison(
    enhancement_id: UUID,
    db: Session = Depends(get_db)
):
    """Get original and enhanced resume for side-by-side comparison.

    Returns both the original resume text and the enhanced markdown text
    for display in the comparison view.

    Args:
        enhancement_id: UUID of the enhancement

    Returns:
        ComparisonResponse with original and enhanced text

    Raises:
        404: Enhancement not found, resume not found, or files missing
        400: Enhanced resume not ready yet
    """

    # Get enhancement
    enhancement = db.query(Enhancement).filter(Enhancement.id == enhancement_id).first()
    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enhancement not found: {enhancement_id}"
        )

    # Get resume
    resume = db.query(Resume).filter(Resume.id == enhancement.resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume not found: {enhancement.resume_id}"
        )

    # Read original resume text
    original_text_path = Path(resume.extracted_text_path)
    if not original_text_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Original resume text not found: {original_text_path}"
        )

    try:
        original_text = original_text_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Failed to read original resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read original resume: {str(e)}"
        )

    # Read enhanced resume markdown
    enhanced_md_path = WORKSPACE_ROOT / "resumes" / "enhanced" / str(enhancement_id) / "enhanced.md"
    if not enhanced_md_path.exists():
        # Check if enhancement is still pending
        if enhancement.status == "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enhancement is still processing. Please wait for it to complete."
            )
        elif enhancement.status == "failed":
            error_msg = enhancement.error_message or "Unknown error"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Enhancement failed: {error_msg}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enhanced resume file not found: {enhanced_md_path}"
            )

    try:
        enhanced_text = enhanced_md_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Failed to read enhanced resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read enhanced resume: {str(e)}"
        )

    logger.info(f"Comparison data retrieved for enhancement {enhancement_id}")

    return {
        'enhancement_id': str(enhancement_id),
        'original_text': original_text,
        'enhanced_text': enhanced_text,
        'enhancement_type': enhancement.enhancement_type,
        'status': enhancement.status
    }
