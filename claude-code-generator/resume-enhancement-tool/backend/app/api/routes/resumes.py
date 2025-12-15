"""Resume API routes."""

import os
import tempfile
import logging
from pathlib import Path
from uuid import UUID
from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Resume
from app.schemas import ResumeResponse, ResumeListResponse
from app.utils.document_parser import DocumentParser
from app.services.workspace_service import WorkspaceService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
WORKSPACE_ROOT = Path("workspace")
workspace_service = WorkspaceService(WORKSPACE_ROOT)
document_parser = DocumentParser()

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/resumes/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    db: Session = Depends(get_db),
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse document: {str(e)}",
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
