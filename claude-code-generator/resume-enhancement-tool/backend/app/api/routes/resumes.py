"""Resume API routes."""

import os
import tempfile
import logging
from pathlib import Path
from uuid import UUID
from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.models import Resume
from app.schemas import ResumeResponse, ResumeListResponse
from app.schemas.style_preview import StyleUpdateRequest, StyleUpdateResponse
from app.utils.document_parser import DocumentParser
from app.utils.error_sanitizer import sanitize_error_message
from app.services.workspace_service import WorkspaceService
from app.config.styles import STYLES
from app.api.dependencies import get_workspace_service, get_document_parser, WORKSPACE_ROOT
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/resumes/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_resume(
    request: Request,
    file: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    db: Session = Depends(get_db),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    document_parser: DocumentParser = Depends(get_document_parser),
):
    """
    Upload a resume file (PDF or DOCX).

    This endpoint:
    1. Validates the file format
    2. Extracts text content from the file
    3. Stores the file in the workspace
    4. Saves metadata to the database

    Returns the created resume with ID and metadata.
    """
    # Validate file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".pdf", ".docx", ".doc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {file_ext}. Only PDF and DOCX are supported.",
        )

    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        content = await file.read()

        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum file size is {MAX_FILE_SIZE / 1024 / 1024:.0f} MB, uploaded file is {len(content) / 1024 / 1024:.1f} MB.",
            )

        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        temp_file.write(content)
        temp_file_path = Path(temp_file.name)

    try:
        # Parse document to extract text
        try:
            parse_result = document_parser.parse_file(temp_file_path)
        except Exception as e:
            # Security: Sanitize error message to prevent PII leakage
            safe_message = sanitize_error_message(e, "document parsing")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse document: {safe_message}",
            )

        extracted_text = parse_result.get("text", "")

        # Calculate word count from extracted text
        word_count = len(extracted_text.split()) if extracted_text else 0

        # Debug logging
        logger.info(f"Parse result: success={parse_result.get('success')}, parser={parse_result.get('parser')}, pages={parse_result.get('pages')}")
        logger.info(f"Extracted text length: {len(extracted_text)} characters, {word_count} words")
        if extracted_text:
            logger.info(f"First 200 chars: {extracted_text[:200]}")

        # Provide more detailed error message
        if not extracted_text:
            error_detail = "No text could be extracted from the document."
            if not parse_result.get("success", False):
                error_detail += f" Parser error: {parse_result.get('error', 'Unknown error')}"
            error_detail += " The PDF may be image-based (scanned) or corrupted."
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail,
            )

        # Validate minimum word count (resumes should have at least 50 words)
        if word_count < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Document appears too short to be a valid resume (only {word_count} words extracted). Resumes must have at least 50 words. The PDF may be image-based or have extraction issues.",
            )

        # Warn if word count is on the lower end (but still valid)
        if word_count < 100:
            logger.warning(f"Resume has only {word_count} words - consider if this is sufficient")

        # Store in workspace
        metadata = {
            "filename": file.filename,
            "original_format": file_ext.replace(".", ""),
            "file_size_bytes": len(content),
            "word_count": word_count,
        }

        resume_id, resume_dir = workspace_service.store_resume(
            temp_file_path,
            extracted_text,
            metadata,
        )

        # Save to database
        db_resume = Resume(
            id=UUID(resume_id),
            filename=file.filename,
            original_format=metadata["original_format"],
            file_path=str(resume_dir / f"source{file_ext}"),
            extracted_text_path=str(resume_dir / "extracted.txt"),
            file_size_bytes=len(content),
            word_count=word_count,
        )

        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)

        return db_resume

    finally:
        # Clean up temporary file
        if temp_file_path.exists():
            os.unlink(temp_file_path)


@router.get("/resumes", response_model=ResumeListResponse)
async def list_resumes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    List all uploaded resumes.

    Query parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100)

    Returns a list of resumes with their metadata.
    """
    resumes = db.query(Resume).offset(skip).limit(limit).all()
    total = db.query(Resume).count()

    return ResumeListResponse(resumes=resumes, total=total)


@router.get("/resumes/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a specific resume by ID.

    Returns the resume metadata including file paths and word count.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume not found: {resume_id}",
        )

    return resume


@router.delete("/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    db: Session = Depends(get_db),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Delete a specific resume by ID.

    This will:
    1. Delete the resume from the database
    2. Delete associated files from workspace
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume not found: {resume_id}",
        )

    # Delete from database
    db.delete(resume)
    db.commit()

    # Delete workspace files using workspace service
    workspace_service.delete_resume(str(resume_id))

    return None


@router.delete("/resumes", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_resumes(
    db: Session = Depends(get_db),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    """
    Delete all resumes from the database and workspace.

    WARNING: This action cannot be undone!
    """
    # Delete all from database
    db.query(Resume).delete()
    db.commit()

    # Delete all workspace files using workspace service
    workspace_service.delete_all_resumes()

    return None


@router.patch("/{resume_id}/update-style", response_model=StyleUpdateResponse)
async def update_resume_style(
    resume_id: UUID,
    style_update: StyleUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    Update the selected writing style for a resume.

    This endpoint allows users to change the writing style after initial selection.
    Can be called from the frontend or as a result of agent recommendation during
    enhancement processing.

    Args:
        resume_id: UUID of the resume to update
        style_update: New style information
        db: Database session

    Returns:
        StyleUpdateResponse with confirmation and old/new styles

    Raises:
        HTTPException: If resume not found or style is invalid
    """
    # Fetch resume
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume not found: {resume_id}",
        )

    # Validate style exists
    if style_update.new_style not in STYLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid style: {style_update.new_style}. "
            f"Valid styles: {', '.join(STYLES.keys())}",
        )

    # Store old style for response
    old_style = resume.selected_style or "none"

    # Update style
    resume.selected_style = style_update.new_style
    resume.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(resume)

    logger.info(
        f"Style updated for resume {resume_id}: "
        f"{old_style} -> {style_update.new_style} "
        f"(source: {style_update.source})"
    )

    if style_update.reason:
        logger.info(f"Reason: {style_update.reason}")

    return StyleUpdateResponse(
        message="Resume style updated successfully",
        resume_id=resume_id,
        old_style=old_style,
        new_style=style_update.new_style,
    )
