"""Job API routes."""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Job
from app.schemas import JobCreate, JobResponse, JobListResponse
from app.services.workspace_service import WorkspaceService

router = APIRouter()

# Initialize services
WORKSPACE_ROOT = Path("workspace")
workspace_service = WorkspaceService(WORKSPACE_ROOT)


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new job description.

    This endpoint:
    1. Validates the job description
    2. Stores it in the workspace
    3. Saves metadata to the database

    Request body should include:
    - title: Job title
    - company: Company name (optional)
    - description_text: Full job description text
    - source: Source of the job description (default: "paste")

    Returns the created job with ID and metadata.
    """
    # Validate job description length
    if len(job.description_text.strip()) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is too short (minimum 50 characters)",
        )

    # Store in workspace
    metadata = {
        "title": job.title,
        "company": job.company,
        "source": job.source,
    }

    job_id, job_dir = workspace_service.store_job(
        job.description_text,
        metadata,
    )

    # Save to database
    db_job = Job(
        id=UUID(job_id),
        title=job.title,
        company=job.company,
        description_text=job.description_text,
        file_path=str(job_dir / "description.txt"),
        source=job.source,
    )

    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    return db_job


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    List all job descriptions.

    Query parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100)

    Returns a list of jobs with their metadata.
    """
    jobs = db.query(Job).offset(skip).limit(limit).all()
    total = db.query(Job).count()

    return JobListResponse(jobs=jobs, total=total)


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a specific job by ID.

    Returns the job metadata including description text and file path.
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        )

    return job
