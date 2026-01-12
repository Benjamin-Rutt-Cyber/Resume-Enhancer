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
from app.utils.error_sanitizer import sanitize_error_message
from app.api.dependencies import get_workspace_service, WORKSPACE_ROOT

logger = logging.getLogger(__name__)

router = APIRouter()


def validate_safe_path(file_path: Path, base_dir: Path) -> bool:
    """
    Validate that file_path is within base_dir (prevent path traversal).

    This security function ensures that file downloads cannot escape the
    workspace directory through path traversal attacks (e.g., ../../etc/passwd).

    Args:
        file_path: The file path to validate
        base_dir: The base directory that the file must be within

    Returns:
        bool: True if path is safe, False otherwise
    """
    try:
        resolved_path = file_path.resolve()
        resolved_base = base_dir.resolve()
        # Check if the resolved path is within the base directory
        return resolved_path.is_relative_to(resolved_base)
    except (ValueError, OSError, RuntimeError) as e:
        logger.warning(f"Path validation failed for {file_path}: {e}")
        return False

# Try to import PDF generator (optional on Windows without GTK)
try:
    from app.utils.pdf_generator import PDFGenerator
    pdf_generator = PDFGenerator(WORKSPACE_ROOT / "templates")
    PDF_AVAILABLE = True
except (ImportError, OSError, TypeError) as e:
    PDF_AVAILABLE = False
    logger.warning(f"PDF generation not available: {e}")
    logger.warning(
        "PDF generation endpoints will not work. "
        "Install GTK libraries or use Docker for PDF support. "
        "Markdown downloads will still work."
    )


@router.post(
    "/enhancements/tailor",
    response_model=EnhancementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tailoring_enhancement(
    enhancement: EnhancementTailorCreate,
    db: Session = Depends(get_db),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
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

    # Create enhancement workspace with user's selected style
    enhancement_id, enhancement_dir = workspace_service.create_enhancement_workspace(
        resume_id=str(enhancement.resume_id),
        job_id=str(enhancement.job_id),
        enhancement_type="job_tailoring",
        style=resume.selected_style,  # Pass the user's selected writing style
    )

    # Save to database
    db_enhancement = Enhancement(
        id=UUID(enhancement_id),
        resume_id=enhancement.resume_id,
        job_id=enhancement.job_id,
        enhancement_type="job_tailoring",
        status="pending",
        run_analysis=enhancement.run_analysis,
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
    workspace_service: WorkspaceService = Depends(get_workspace_service),
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

    # Create enhancement workspace with user's selected style
    enhancement_id, enhancement_dir = workspace_service.create_enhancement_workspace(
        resume_id=str(enhancement.resume_id),
        job_id=None,
        enhancement_type="industry_revamp",
        industry=enhancement.industry,
        style=resume.selected_style,  # Pass the user's selected writing style
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
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Get a specific enhancement by ID.

    Automatically detects completion of both resume and cover letter.

    Returns the enhancement metadata including status, output paths, and timestamps.

    The status can be:
    - "pending": Waiting for Claude Code to process
    - "completed": Enhancement finished successfully
    - "failed": Enhancement failed (check error_message)

    Cover letter status can be:
    - "pending": Resume not complete yet
    - "in_progress": Resume complete, generating cover letter
    - "completed": Cover letter ready for download
    - "failed": Cover letter generation failed
    - "skipped": No cover letter (industry revamp)
    """
    enhancement = db.query(Enhancement).filter(Enhancement.id == enhancement_id).first()

    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enhancement not found: {enhancement_id}",
        )

    # Use completion detector to check status of both resume and cover letter
    from app.services.completion_detector import CompletionDetectorService
    detector = CompletionDetectorService(workspace_service)
    detector.check_and_update_enhancement(enhancement, db)

    # Refresh from database after potential updates
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
            enhanced_md_path,
            pdf_path,
        )

        # Update enhancement record
        enhancement.output_path = str(enhanced_md_path)
        enhancement.pdf_path = str(pdf_path)
        enhancement.status = "completed"
        enhancement.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(enhancement)

        return enhancement

    except (IOError, OSError) as e:
        # File system errors
        safe_message = sanitize_error_message(e, "PDF generation - file system")
        enhancement.status = "failed"
        enhancement.error_message = safe_message
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File system error during PDF generation",
        )
    except ValueError as e:
        # Invalid markdown content
        safe_message = sanitize_error_message(e, "PDF generation - invalid content")
        enhancement.status = "failed"
        enhancement.error_message = safe_message
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid markdown content for PDF generation",
        )
    except Exception as e:
        # Unexpected errors - log and fail gracefully
        safe_message = sanitize_error_message(e, "PDF generation - unexpected")
        enhancement.status = "failed"
        enhancement.error_message = safe_message
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during PDF generation",
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

        # Security: Validate path to prevent traversal attacks
        pdf_path = Path(enhancement.pdf_path)
        if not validate_safe_path(pdf_path, WORKSPACE_ROOT):
            logger.error(f"Path traversal attempt detected: {pdf_path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path"
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

        # Security: Validate path to prevent traversal attacks
        md_path = Path(enhancement.output_path)
        if not validate_safe_path(md_path, WORKSPACE_ROOT):
            logger.error(f"Path traversal attempt detected: {md_path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path"
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


@router.get("/enhancements/{enhancement_id}/download/docx")
async def download_enhancement_docx(
    enhancement_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Download the enhanced resume as DOCX.

    Converts the enhanced markdown to a styled Word document.
    The DOCX is generated on first request and cached for subsequent requests.

    Returns:
        FileResponse with DOCX file
    """
    from app.utils.docx_generator import DOCXGenerator

    docx_generator = DOCXGenerator()

    enhancement = db.query(Enhancement).filter(Enhancement.id == enhancement_id).first()
    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enhancement not found: {enhancement_id}"
        )

    # Check if DOCX already exists (cached)
    if enhancement.docx_path and Path(enhancement.docx_path).exists():
        logger.info(f"Returning cached DOCX for enhancement {enhancement_id}")

        # Security: Validate path to prevent traversal attacks
        docx_path = Path(enhancement.docx_path)
        if not validate_safe_path(docx_path, WORKSPACE_ROOT):
            logger.error(f"Path traversal attempt detected: {docx_path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path"
            )

        return FileResponse(
            path=enhancement.docx_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"enhanced_resume_{enhancement_id}.docx"
        )

    # Check if markdown file exists
    enhanced_md_path = WORKSPACE_ROOT / "resumes" / "enhanced" / str(enhancement_id) / "enhanced.md"
    if not enhanced_md_path.exists():
        if enhancement.status == "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enhancement is still processing. Please wait for it to complete."
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enhanced markdown file not found. Enhancement may not be complete."
        )

    # Generate DOCX from markdown
    docx_path = WORKSPACE_ROOT / "resumes" / "enhanced" / str(enhancement_id) / "enhanced.docx"

    try:
        logger.info(f"Generating DOCX for enhancement {enhancement_id}")
        docx_generator.markdown_to_docx(enhanced_md_path, docx_path)

        # Update enhancement record with DOCX path
        enhancement.docx_path = str(docx_path)
        db.commit()

        logger.info(f"DOCX generated successfully for enhancement {enhancement_id}")

        # Security: Validate path to prevent traversal attacks
        if not validate_safe_path(docx_path, WORKSPACE_ROOT):
            logger.error(f"Path traversal attempt detected: {docx_path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path"
            )

        return FileResponse(
            path=str(docx_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"enhanced_resume_{enhancement_id}.docx"
        )

    except (IOError, OSError) as e:
        # File system errors
        safe_message = sanitize_error_message(e, "DOCX generation - file system")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File system error during DOCX generation"
        )
    except ValueError as e:
        # Invalid markdown content
        safe_message = sanitize_error_message(e, "DOCX generation - invalid content")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid markdown content for DOCX generation"
        )
    except Exception as e:
        # Unexpected errors - log and fail gracefully
        safe_message = sanitize_error_message(e, "DOCX generation - unexpected")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during DOCX generation"
        )


@router.delete("/enhancements/{enhancement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enhancement(
    enhancement_id: UUID,
    db: Session = Depends(get_db),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Delete a specific enhancement by ID.

    This will:
    1. Delete the enhancement from the database
    2. Delete associated files from workspace
    """
    enhancement = db.query(Enhancement).filter(Enhancement.id == enhancement_id).first()

    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enhancement not found: {enhancement_id}",
        )

    # Delete from database
    db.delete(enhancement)
    db.commit()

    # Delete workspace files using workspace service
    workspace_service.delete_enhancement(str(enhancement_id))

    return None


@router.delete("/enhancements", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_enhancements(
    db: Session = Depends(get_db),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Delete all enhancements from the database and workspace.

    WARNING: This action cannot be undone!
    """
    # Delete all from database
    db.query(Enhancement).delete()
    db.commit()

    # Delete all workspace files using workspace service
    workspace_service.delete_all_enhancements()

    return None


@router.get("/enhancements/{enhancement_id}/download/cover-letter")
async def download_cover_letter(
    enhancement_id: UUID,
    format: str = "md",
    db: Session = Depends(get_db),
):
    """
    Download the cover letter in specified format.

    Query parameters:
    - format: "md" (default), "pdf", or "docx"

    Returns the file as a download attachment.

    The cover letter is generated automatically after the resume is complete.
    DOCX and PDF formats are generated lazily on first request and cached.
    """
    enhancement = db.query(Enhancement).filter(Enhancement.id == enhancement_id).first()

    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enhancement not found: {enhancement_id}"
        )

    # Check cover letter status
    if enhancement.cover_letter_status == "skipped":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cover letter not available for industry revamp enhancements. Only job tailoring includes cover letters."
        )

    if enhancement.cover_letter_status != "completed":
        status_messages = {
            "pending": "Resume is still being generated. Cover letter will be available after resume completes.",
            "in_progress": "Cover letter is currently being generated. Please check back in a moment.",
            "failed": f"Cover letter generation failed: {enhancement.cover_letter_error or 'Unknown error'}"
        }
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=status_messages.get(enhancement.cover_letter_status, f"Cover letter not ready. Status: {enhancement.cover_letter_status}")
        )

    # Get cover letter markdown path
    cover_letter_md = WORKSPACE_ROOT / "resumes" / "enhanced" / str(enhancement_id) / "cover_letter.md"

    if not cover_letter_md.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter file not found on disk despite completed status. Please contact support."
        )

    # Format-specific handling
    if format == "md":
        # Security: Validate path to prevent traversal attacks
        if not validate_safe_path(cover_letter_md, WORKSPACE_ROOT):
            logger.error(f"Path traversal attempt detected: {cover_letter_md}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path"
            )

        return FileResponse(
            path=str(cover_letter_md),
            media_type="text/markdown",
            filename=f"cover_letter_{enhancement_id}.md"
        )

    elif format == "docx":
        # Lazy DOCX generation with caching
        docx_path = WORKSPACE_ROOT / "resumes" / "enhanced" / str(enhancement_id) / "cover_letter.docx"

        if not docx_path.exists():
            logger.info(f"Generating DOCX for cover letter {enhancement_id}")
            from app.utils.docx_generator import DOCXGenerator
            docx_generator = DOCXGenerator()
            docx_generator.markdown_to_docx(cover_letter_md, docx_path)

            # Cache path in database
            enhancement.cover_letter_docx_path = str(docx_path)
            db.commit()
        else:
            logger.info(f"Returning cached DOCX for cover letter {enhancement_id}")

        # Security: Validate path to prevent traversal attacks
        if not validate_safe_path(docx_path, WORKSPACE_ROOT):
            logger.error(f"Path traversal attempt detected: {docx_path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path"
            )

        return FileResponse(
            path=str(docx_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"cover_letter_{enhancement_id}.docx"
        )

    elif format == "pdf":
        # Check if PDF generation is available
        if not PDF_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="PDF generation not available on this system. Please use Docker or install GTK libraries. You can still download markdown or DOCX versions."
            )

        # Lazy PDF generation with caching
        pdf_path = WORKSPACE_ROOT / "resumes" / "enhanced" / str(enhancement_id) / "cover_letter.pdf"

        if not pdf_path.exists():
            logger.info(f"Generating PDF for cover letter {enhancement_id}")
            pdf_generator.markdown_to_pdf(str(cover_letter_md), str(pdf_path))

            # Cache path in database
            enhancement.cover_letter_pdf_path = str(pdf_path)
            db.commit()
        else:
            logger.info(f"Returning cached PDF for cover letter {enhancement_id}")

        # Security: Validate path to prevent traversal attacks
        if not validate_safe_path(pdf_path, WORKSPACE_ROOT):
            logger.error(f"Path traversal attempt detected: {pdf_path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path"
            )

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=f"cover_letter_{enhancement_id}.pdf"
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format: {format}. Must be 'md', 'pdf', or 'docx'"
        )
