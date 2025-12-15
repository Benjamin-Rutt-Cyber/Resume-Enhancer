"""
Pytest configuration and fixtures for Resume Enhancement Tool tests.

This module provides reusable fixtures for testing:
- Database session (in-memory SQLite)
- FastAPI test client
- Temporary workspace directories
- Sample test data (PDFs, DOCX files)
- Mock data for models
"""

import os
import tempfile
from pathlib import Path
from typing import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Import application components
from app.core.database import Base, get_db
from main import app  # app is in backend/main.py, not app/main.py
from app.models import Resume, Job, Enhancement
from app.services.workspace_service import WorkspaceService
from app.utils.document_parser import DocumentParser


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create an in-memory SQLite database for testing.

    This fixture creates a fresh database for each test function,
    ensuring test isolation.

    Yields:
        Session: SQLAlchemy database session
    """
    # Create in-memory SQLite engine
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Required for in-memory SQLite with threads
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create session
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> TestClient:
    """
    Create FastAPI test client with test database.

    This overrides the get_db dependency to use the test database
    instead of the production database.

    Args:
        test_db: Test database session fixture

    Returns:
        TestClient: FastAPI test client
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass  # Session cleanup handled by test_db fixture

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()


# ============================================================================
# Workspace Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def temp_workspace(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Create temporary workspace directory for file operations.

    Creates the full workspace directory structure:
    - resumes/original/
    - resumes/enhanced/
    - jobs/
    - templates/
    - _instructions/industries/

    Args:
        tmp_path: pytest's built-in temporary path fixture

    Yields:
        Path: Root path of temporary workspace
    """
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()

    # Create subdirectories
    (workspace_root / "resumes" / "original").mkdir(parents=True)
    (workspace_root / "resumes" / "enhanced").mkdir(parents=True)
    (workspace_root / "jobs").mkdir(parents=True)
    (workspace_root / "templates").mkdir(parents=True)
    (workspace_root / "_instructions" / "industries").mkdir(parents=True)

    # Create sample industry guide for testing
    industry_guide_content = """
    # IT Industry Resume Guide

    ## Key Skills
    - Programming languages
    - Cloud platforms
    - DevOps tools

    ## Best Practices
    - Quantify achievements
    - Include technical certifications
    """

    (workspace_root / "_instructions" / "industries" / "it.md").write_text(
        industry_guide_content
    )

    yield workspace_root

    # Cleanup handled by tmp_path


@pytest.fixture(scope="function")
def workspace_service(temp_workspace: Path) -> WorkspaceService:
    """
    Create WorkspaceService instance with temporary workspace.

    Args:
        temp_workspace: Temporary workspace path fixture

    Returns:
        WorkspaceService: Configured workspace service
    """
    return WorkspaceService(temp_workspace)


# ============================================================================
# Document Parser Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def document_parser() -> DocumentParser:
    """
    Create DocumentParser instance.

    Returns:
        DocumentParser: Document parser instance
    """
    return DocumentParser()


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def sample_resume_text() -> str:
    """
    Sample resume text for testing.

    Returns:
        str: Resume text with 100+ words
    """
    return """
    John Doe
    Software Engineer
    john.doe@email.com | (555) 123-4567 | LinkedIn: johndoe

    SUMMARY
    Experienced software engineer with 5+ years of expertise in full-stack development,
    cloud architecture, and agile methodologies. Proven track record of delivering
    scalable applications and leading cross-functional teams.

    EXPERIENCE
    Senior Software Engineer | Tech Company Inc. | 2020 - Present
    - Led development of microservices architecture serving 1M+ users
    - Reduced API response time by 40% through optimization
    - Mentored team of 5 junior developers

    Software Engineer | StartUp Co. | 2018 - 2020
    - Built RESTful APIs using Python and FastAPI
    - Implemented CI/CD pipeline reducing deployment time by 60%
    - Collaborated with product team on feature development

    EDUCATION
    B.S. Computer Science | University Name | 2018

    SKILLS
    Languages: Python, JavaScript, TypeScript, SQL
    Frameworks: FastAPI, React, Node.js
    Tools: Docker, Kubernetes, AWS, PostgreSQL

    CERTIFICATIONS
    - AWS Certified Solutions Architect
    - Certified Kubernetes Administrator
    """


@pytest.fixture(scope="function")
def sample_pdf(tmp_path: Path, sample_resume_text: str) -> Path:
    """
    Create sample PDF file for testing.

    Args:
        tmp_path: pytest's built-in temporary path fixture
        sample_resume_text: Sample resume text

    Returns:
        Path: Path to created PDF file
    """
    # Note: Creating a real PDF requires additional libraries
    # For testing, we'll create a text file that can be used with mocked parsers
    pdf_path = tmp_path / "sample_resume.pdf"

    # In real tests, you would use reportlab or pypdf to create actual PDFs
    # For now, create a placeholder
    pdf_path.write_text(sample_resume_text)

    return pdf_path


@pytest.fixture(scope="function")
def sample_docx(tmp_path: Path, sample_resume_text: str) -> Path:
    """
    Create sample DOCX file for testing.

    Args:
        tmp_path: pytest's built-in temporary path fixture
        sample_resume_text: Sample resume text

    Returns:
        Path: Path to created DOCX file
    """
    docx_path = tmp_path / "sample_resume.docx"

    # In real tests, you would use python-docx to create actual DOCX files
    # For now, create a placeholder
    docx_path.write_text(sample_resume_text)

    return docx_path


@pytest.fixture(scope="function")
def mock_resume_data() -> dict:
    """
    Mock resume data for testing.

    Returns:
        dict: Resume data dictionary
    """
    return {
        "filename": "test_resume.pdf",
        "text": "John Doe Software Engineer with 5 years experience in Python development.",
        "word_count": 150,
        "file_size_bytes": 50000,
    }


@pytest.fixture(scope="function")
def sample_job_description() -> str:
    """
    Sample job description for testing.

    Returns:
        str: Job description text
    """
    return """
    Desktop Support Engineer

    Total IT Global is seeking a Desktop Support Engineer to join our team.

    Responsibilities:
    - Provide technical support to end users
    - Troubleshoot hardware and software issues
    - Install and configure computer systems
    - Maintain IT documentation

    Requirements:
    - 2+ years experience in IT support
    - Strong knowledge of Windows and Mac OS
    - Excellent communication skills
    - CompTIA A+ certification preferred

    Skills:
    - Windows 10/11
    - Active Directory
    - Microsoft Office 365
    - Remote desktop support
    """


# ============================================================================
# Model Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_resume(test_db: Session) -> Resume:
    """
    Create test resume record in database.

    Args:
        test_db: Test database session

    Returns:
        Resume: Created resume model instance
    """
    resume = Resume(
        id=uuid4(),
        filename="test_resume.pdf",
        original_format="pdf",
        file_path="/workspace/resumes/original/test-001/source.pdf",
        extracted_text_path="/workspace/resumes/original/test-001/extracted.txt",
        file_size_bytes=50000,
        word_count=150,
    )
    test_db.add(resume)
    test_db.commit()
    test_db.refresh(resume)
    return resume


@pytest.fixture(scope="function")
def test_job(test_db: Session) -> Job:
    """
    Create test job record in database.

    Args:
        test_db: Test database session

    Returns:
        Job: Created job model instance
    """
    job = Job(
        id=uuid4(),
        title="Software Engineer",
        company="Tech Company Inc.",
        description="We are looking for a software engineer...",
        source="company_website",
    )
    test_db.add(job)
    test_db.commit()
    test_db.refresh(job)
    return job


@pytest.fixture(scope="function")
def test_enhancement(test_db: Session, test_resume: Resume, test_job: Job) -> Enhancement:
    """
    Create test enhancement record in database.

    Args:
        test_db: Test database session
        test_resume: Test resume fixture
        test_job: Test job fixture

    Returns:
        Enhancement: Created enhancement model instance
    """
    enhancement = Enhancement(
        id=uuid4(),
        resume_id=test_resume.id,
        job_id=test_job.id,
        enhancement_type="job_tailoring",
        status="pending",
    )
    test_db.add(enhancement)
    test_db.commit()
    test_db.refresh(enhancement)
    return enhancement


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def test_env():
    """
    Set up test environment variables.

    This fixture runs once per test session and sets up
    environment variables needed for testing.
    """
    # Set test environment variables
    os.environ["DEBUG"] = "True"
    os.environ["SECRET_KEY"] = "test-secret-key-32-characters-minimum-length-required"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    yield

    # Cleanup not needed for session-scoped fixture
