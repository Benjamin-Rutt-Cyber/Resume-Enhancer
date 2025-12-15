"""Enhancement API routes."""

import logging
from pathlib import Path
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Enhancement, Resume, Job
from app.schemas import (
    EnhancementTailorCreate,
    EnhancementRevampCreate,
    EnhancementResponse,
    EnhancementListResponse,
)
from app.services.workspace_service import WorkspaceService

logger = logging.getLogger(__name__)

# Try to import PDF generator (optional on Windows without GTK)
try:
    from app.utils.pdf_generator import PDFGenerator
    pdf_generator = PDFGenerator()
    PDF_AVAILABLE = True
except (ImportError, OSError) as e:
    PDF_AVAILABLE = False
    logger.warning(f"PDF generation not available: {e}")
    logger.warning(
        "PDF generation endpoints will not work. "
        "Install GTK libraries or use Docker for PDF support. "
        "Markdown downloads will still work."
    )

router = APIRouter()

# Initialize services
WORKSPACE_ROOT = Path("workspace")
workspace_service = WorkspaceService(WORKSPACE_ROOT)


@router.post(
    "/enhancements/tailor",
    response_model=EnhancementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tailoring_enhancement(
    enhancement: EnhancementTailorCreate,
    db: Session = Depends(get_db),
):
    """
    Create a job-tailoring enhancement request.

    This endpoint:
    1. Validates that the resume and job exist
    2. Creates an enhancement workspace with INSTRUCTIONS.md
    3. Returns the enhancement ID for tracking

    The actual enhancement is performed by Claude Code reading the INSTRUCTIONS.md file.

    Request body:
    - resume_id: ID of the resume to enhance
    - job_id: ID of the job to tailor the resume for
    - enhancement_type: Must be "job_tailoring"

    Returns the enhancement record with status "pending".
    """
    # Verify resume exists
    resume = db.query(Resume).filter(Resume.id == enhancement.resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume not found: {enhancement.resume_id}",
        )

    # Verify job exists
    job = db.query(Job).filter(Job.id == enhancement.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {enhancement.job_id}",
        )

    # Create enhancement workspace
    enhancement_id, enhancement_dir = workspace_service.create_enhancement_workspace(
        resume_id=str(enhancement.resume_id),
        job_id=str(enhancement.job_id),
        enhancement_type="job_tailoring",
    )

    # Save to database
    db_enhancement = Enhancement(
        id=UUID(enhancement_id),
        resume_id=enhancement.resume_id,
        job_id=enhancement.job_id,
        enhancement_type="job_tailoring",
        status="pending",
    )

    db.add(db_enhancement)
    db.commit()
    db.refresh(db_enhancement)

    return db_enhancement


@router.post(
    "/enhancements/revamp",
    response_model=EnhancementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_revamp_enhancement(
    enhancement: EnhancementRevampCreate,
    db: Session = Depends(get_db),
):
    """
    Create an industry-revamp enhancement request.

    This endpoint:
    1. Validates that the resume exists
    2. Validates the industry (IT, Cybersecurity, Finance)
    3. Creates an enhancement workspace with INSTRUCTIONS.md
    4. Returns the enhancement ID for tracking

    The actual enhancement is performed by Claude Code reading the INSTRUCTIONS.md file.

    Request body:
    - resume_id: ID of the resume to enhance
    - industry: Target industry (IT, Cybersecurity, Finance)

    Returns the enhancement record with status "pending".
    """
    # Verify resume exists
    resume = db.query(Resume).filter(Resume.id == enhancement.resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume not found: {enhancement.resume_id}",
        )

    # Validate industry
    valid_industries = ["IT", "Cybersecurity", "Finance"]
    if enhancement.industry not in valid_industries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid industry. Must be one of: {', '.join(valid_industries)}",
        )

    # Create enhancement workspace
    enhancement_id, enhancement_dir = workspace_service.create_enhancement_workspace(
        resume_id=str(enhancement.resume_id),
        job_id=None,
        enhancement_type="industry_revamp",
        industry=enhancement.industry,
    )

    # Save to database
    db_enhancement = Enhancement(
        id=UUID(enhancement_id),
        resume_id=enhancement.resume_id,
        job_id=None,
        enhancement_type="industry_revamp",
        industry=enhancement.industry,
        status="pending",
    )

    db.add(db_enhancement)
    db.commit()
    db.refresh(db_enhancement)

    return db_enhancement


@router.get("/enhancements", response_model=EnhancementListResponse)
async def list_enhancements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    List all enhancement requests.

    Query parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100)

    Returns a list of enhancements with their metadata and status.
    """
    enhancements = db.query(Enhancement).offset(skip).limit(limit).all()
    total = db.query(Enhancement).count()

    return EnhancementListResponse(enhancements=enhancements, total=total)


@router.get("/enhancements/{enhancement_id}", response_model=EnhancementResponse)
async def get_enhancement(
    enhancement_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a specific enhancement by ID.

    Returns the enhancement metadata including status, output paths, and timestamps.

    The status can be:
    - "pending": Waiting for Claude Code to process
    - "completed": Enhancement finished successfully
    - "failed": Enhancement failed (check error_message)
    """
    enhancement = db.query(Enhancement).filter(Enhancement.id == enhancement_id).first()

    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enhancement not found: {enhancement_id}",
        )

    # Check if enhanced markdown file exists and update status
    enhanced_md_path = WORKSPACE_ROOT / "resumes" / "enhanced" / str(enhancement_id) / "enhanced.md"
    if enhanced_md_path.exists() and enhancement.status == "pending":
        enhancement.status = "completed"
        enhancement.completed_at = datetime.utcnow()
        enhancement.output_path = str(enhanced_md_path)
        db.commit()
        db.refresh(enhancement)

    return enhancement


@router.post("/enhancements/{enhancement_id}/finalize")
async def finalize_enhancement(
    enhancement_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Finalize an enhancement by generating the PDF from the markdown.

    This endpoint:
    1. Checks that the enhancement markdown exists
    2. Converts the markdown to PDF
    3. Updates the enhancement record with PDF path
    4. Marks the enhancement as completed

    Returns the updated enhancement record.
    """
    enhancement = db.query(Enhancement).filter(Enhancement.id == enhancement_id).first()

    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enhancement not found: {enhancement_id}",
        )

    # Check if markdown file exists
    enhanced_md_path = WORKSPACE_ROOT / "resumes" / "enhanced" / str(enhancement_id) / "enhanced.md"
    if not enhanced_md_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enhanced markdown file not found. Please wait for Claude Code to complete the enhancement.",
        )

    # Check if PDF generation is available
    if not PDF_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF generation is not available on this system. Please use Docker or install GTK libraries. You can still download the markdown version.",
        )

    # Generate PDF
    try:
        pdf_path = WORKSPACE_ROOT / "resumes" / "enhanced" / str(enhancement_id) / "enhanced.pdf"
        pdf_generator.markdown_to_pdf(
            str(enhanced_md_path),
            str(pdf_path),
        )

        # Update enhancement record
        enhancement.output_path = str(enhanced_md_path)
        enhancement.pdf_path = str(pdf_path)
        enhancement.status = "completed"
        enhancement.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(enhancement)

        return enhancement

    except Exception as e:
        enhancement.status = "failed"
        enhancement.error_message = str(e)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}",
        )


@router.get("/enhancements/{enhancement_id}/download")
async def download_enhancement(
    enhancement_id: UUID,
    format: str = "pdf",
    db: Session = Depends(get_db),
):
    """
    Download the enhanced resume.

    Query parameters:
    - format: "pdf" (default) or "md" for markdown

    Returns the file as a download attachment.
    """
    enhancement = db.query(Enhancement).filter(Enhancement.id == enhancement_id).first()

    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enhancement not found: {enhancement_id}",
        )

    if format == "pdf":
        if not enhancement.pdf_path or not Path(enhancement.pdf_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF file not found. Please finalize the enhancement first using POST /enhancements/{id}/finalize",
            )

        return FileResponse(
            path=enhancement.pdf_path,
            media_type="application/pdf",
            filename=f"enhanced_resume_{enhancement_id}.pdf",
        )

    elif format == "md":
        if not enhancement.output_path or not Path(enhancement.output_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Markdown file not found. Enhancement may not be complete yet.",
            )

        return FileResponse(
            path=enhancement.output_path,
            media_type="text/markdown",
            filename=f"enhanced_resume_{enhancement_id}.md",
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format: {format}. Must be 'pdf' or 'md'",
        )
