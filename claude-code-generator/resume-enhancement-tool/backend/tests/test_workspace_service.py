"""
Tests for WorkspaceService - File operations and workspace management.

This module tests the workspace service responsible for:
- Creating workspace directory structure
- Storing resumes and jobs
- Creating enhancement workspaces with INSTRUCTIONS.md
- Checking enhancement completion status
- Managing file paths
"""

import json
import pytest
from pathlib import Path
from uuid import uuid4

from app.services.workspace_service import WorkspaceService
from tests.utils import (
    create_test_pdf,
    SAMPLE_RESUME_VALID,
    SAMPLE_JOB_DESCRIPTION,
)


class TestWorkspaceInitialization:
    """Test workspace service initialization and directory creation."""

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_init_creates_directory_structure(self, temp_workspace):
        """Test that initialization creates all required directories."""
        service = WorkspaceService(temp_workspace)

        # Verify all required directories exist
        expected_dirs = [
            "resumes/original",
            "resumes/enhanced",
            "jobs",
            "templates/resume_formats",
            "templates/styles",
            "_instructions/industries",
        ]

        for dir_path in expected_dirs:
            full_path = temp_workspace / dir_path
            assert full_path.exists(), f"Directory not created: {dir_path}"
            assert full_path.is_dir(), f"Path is not a directory: {dir_path}"

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_init_with_nonexistent_workspace(self, tmp_path):
        """Test initialization creates workspace if it doesn't exist."""
        workspace_path = tmp_path / "new_workspace"
        assert not workspace_path.exists()

        service = WorkspaceService(workspace_path)

        # Workspace should be created
        assert workspace_path.exists()
        assert (workspace_path / "resumes" / "original").exists()


class TestStoreResume:
    """Test resume storage functionality."""

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_store_resume_creates_workspace(self, workspace_service, tmp_path):
        """Test that storing a resume creates proper workspace structure."""
        # Create a test PDF
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "test.pdf")

        metadata = {
            "filename": "test_resume.pdf",
            "original_format": "pdf",
            "file_size_bytes": pdf_path.stat().st_size,
            "word_count": 150,
        }

        resume_id, resume_dir = workspace_service.store_resume(
            file_path=pdf_path,
            extracted_text=SAMPLE_RESUME_VALID,
            metadata=metadata,
        )

        # Verify resume ID is a valid UUID
        assert len(resume_id) == 36  # UUID string length

        # Verify directory was created
        assert resume_dir.exists()
        assert resume_dir.is_dir()

        # Verify directory is in correct location
        assert resume_dir.parent.name == "original"
        assert resume_dir.parent.parent.name == "resumes"

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_store_resume_copies_source_file(self, workspace_service, tmp_path):
        """Test that the original resume file is copied."""
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "test.pdf")

        metadata = {"filename": "test_resume.pdf", "original_format": "pdf"}

        resume_id, resume_dir = workspace_service.store_resume(
            file_path=pdf_path,
            extracted_text=SAMPLE_RESUME_VALID,
            metadata=metadata,
        )

        # Verify source file was copied
        source_file = resume_dir / "source.pdf"
        assert source_file.exists()
        assert source_file.stat().st_size > 0

        # Original file should still exist
        assert pdf_path.exists()

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_store_resume_creates_extracted_txt(self, workspace_service, tmp_path):
        """Test that extracted text is saved to extracted.txt."""
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "test.pdf")

        metadata = {"filename": "test_resume.pdf"}

        resume_id, resume_dir = workspace_service.store_resume(
            file_path=pdf_path,
            extracted_text=SAMPLE_RESUME_VALID,
            metadata=metadata,
        )

        # Verify extracted.txt exists and contains correct text
        extracted_file = resume_dir / "extracted.txt"
        assert extracted_file.exists()

        content = extracted_file.read_text(encoding="utf-8")
        assert content == SAMPLE_RESUME_VALID

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_store_resume_creates_metadata(self, workspace_service, tmp_path):
        """Test that metadata.json is created with correct information."""
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "test.pdf")

        metadata = {
            "filename": "test_resume.pdf",
            "original_format": "pdf",
            "word_count": 150,
        }

        resume_id, resume_dir = workspace_service.store_resume(
            file_path=pdf_path,
            extracted_text=SAMPLE_RESUME_VALID,
            metadata=metadata,
        )

        # Verify metadata.json exists
        metadata_file = resume_dir / "metadata.json"
        assert metadata_file.exists()

        # Verify metadata content
        with open(metadata_file, "r", encoding="utf-8") as f:
            saved_metadata = json.load(f)

        assert saved_metadata["filename"] == "test_resume.pdf"
        assert saved_metadata["original_format"] == "pdf"
        assert saved_metadata["word_count"] == 150
        assert saved_metadata["resume_id"] == resume_id
        assert "stored_at" in saved_metadata
        assert saved_metadata["source_file"] == "source.pdf"

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_store_resume_docx_format(self, workspace_service, tmp_path):
        """Test storing DOCX format resume."""
        from tests.utils import create_test_docx

        docx_path = create_test_docx(SAMPLE_RESUME_VALID, tmp_path / "test.docx")

        metadata = {"filename": "test_resume.docx", "original_format": "docx"}

        resume_id, resume_dir = workspace_service.store_resume(
            file_path=docx_path,
            extracted_text=SAMPLE_RESUME_VALID,
            metadata=metadata,
        )

        # Verify source file has .docx extension
        source_file = resume_dir / "source.docx"
        assert source_file.exists()


class TestStoreJob:
    """Test job description storage functionality."""

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_store_job_creates_workspace(self, workspace_service):
        """Test that storing a job creates proper workspace structure."""
        metadata = {
            "title": "Software Engineer",
            "company": "Tech Company Inc.",
            "source": "company_website",
        }

        job_id, job_dir = workspace_service.store_job(
            description=SAMPLE_JOB_DESCRIPTION,
            metadata=metadata,
        )

        # Verify job ID is a valid UUID
        assert len(job_id) == 36

        # Verify directory was created
        assert job_dir.exists()
        assert job_dir.is_dir()

        # Verify directory is in correct location
        assert job_dir.parent.name == "jobs"

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_store_job_saves_description(self, workspace_service):
        """Test that job description is saved to description.txt."""
        metadata = {"title": "Software Engineer"}

        job_id, job_dir = workspace_service.store_job(
            description=SAMPLE_JOB_DESCRIPTION,
            metadata=metadata,
        )

        # Verify description.txt exists and contains correct text
        description_file = job_dir / "description.txt"
        assert description_file.exists()

        content = description_file.read_text(encoding="utf-8")
        assert content == SAMPLE_JOB_DESCRIPTION

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_store_job_creates_metadata(self, workspace_service):
        """Test that job metadata.json is created correctly."""
        metadata = {
            "title": "Desktop Support Engineer",
            "company": "Total IT Global",
            "source": "job_board",
        }

        job_id, job_dir = workspace_service.store_job(
            description=SAMPLE_JOB_DESCRIPTION,
            metadata=metadata,
        )

        # Verify metadata.json exists
        metadata_file = job_dir / "metadata.json"
        assert metadata_file.exists()

        # Verify metadata content
        with open(metadata_file, "r", encoding="utf-8") as f:
            saved_metadata = json.load(f)

        assert saved_metadata["title"] == "Desktop Support Engineer"
        assert saved_metadata["company"] == "Total IT Global"
        assert saved_metadata["source"] == "job_board"
        assert saved_metadata["job_id"] == job_id
        assert "stored_at" in saved_metadata


class TestCreateEnhancementWorkspace:
    """Test enhancement workspace creation."""

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_create_enhancement_workspace_job_tailoring(self, workspace_service):
        """Test creating job tailoring enhancement workspace."""
        resume_id = str(uuid4())
        job_id = str(uuid4())

        enhancement_id, enhancement_dir = workspace_service.create_enhancement_workspace(
            resume_id=resume_id,
            job_id=job_id,
            enhancement_type="job_tailoring",
        )

        # Verify enhancement ID is valid UUID
        assert len(enhancement_id) == 36

        # Verify directory created
        assert enhancement_dir.exists()
        assert enhancement_dir.is_dir()

        # Verify directory is in correct location
        assert enhancement_dir.parent.name == "enhanced"

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_create_enhancement_workspace_creates_instructions(self, workspace_service):
        """Test that INSTRUCTIONS.md is created."""
        resume_id = str(uuid4())
        job_id = str(uuid4())

        enhancement_id, enhancement_dir = workspace_service.create_enhancement_workspace(
            resume_id=resume_id,
            job_id=job_id,
            enhancement_type="job_tailoring",
        )

        # Verify INSTRUCTIONS.md exists
        instructions_file = enhancement_dir / "INSTRUCTIONS.md"
        assert instructions_file.exists()

        # Verify instructions content
        content = instructions_file.read_text(encoding="utf-8")
        assert "Resume Enhancement Request" in content
        assert "Job-Specific Tailoring" in content
        assert resume_id in content
        assert job_id in content
        assert f"workspace/resumes/original/{resume_id}/extracted.txt" in content
        assert f"workspace/jobs/{job_id}/description.txt" in content
        assert f"workspace/resumes/enhanced/{enhancement_id}/enhanced.md" in content

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_create_enhancement_workspace_industry_revamp(self, workspace_service):
        """Test creating industry revamp enhancement workspace."""
        resume_id = str(uuid4())

        enhancement_id, enhancement_dir = workspace_service.create_enhancement_workspace(
            resume_id=resume_id,
            job_id=None,
            enhancement_type="industry_revamp",
            industry="Information Technology",
        )

        # Verify INSTRUCTIONS.md exists
        instructions_file = enhancement_dir / "INSTRUCTIONS.md"
        assert instructions_file.exists()

        # Verify instructions content
        content = instructions_file.read_text(encoding="utf-8")
        assert "Industry-Focused Revamp" in content
        assert "Information Technology" in content
        assert resume_id in content
        assert "industry guide" in content.lower()

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_create_enhancement_workspace_creates_metadata(self, workspace_service):
        """Test that enhancement metadata.json is created."""
        resume_id = str(uuid4())
        job_id = str(uuid4())

        enhancement_id, enhancement_dir = workspace_service.create_enhancement_workspace(
            resume_id=resume_id,
            job_id=job_id,
            enhancement_type="job_tailoring",
        )

        # Verify metadata.json exists
        metadata_file = enhancement_dir / "metadata.json"
        assert metadata_file.exists()

        # Verify metadata content
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        assert metadata["enhancement_id"] == enhancement_id
        assert metadata["resume_id"] == resume_id
        assert metadata["job_id"] == job_id
        assert metadata["enhancement_type"] == "job_tailoring"
        assert metadata["status"] == "pending"
        assert "created_at" in metadata

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_create_enhancement_workspace_invalid_type(self, workspace_service):
        """Test that invalid enhancement type raises error."""
        resume_id = str(uuid4())

        with pytest.raises(ValueError, match="Unknown enhancement type"):
            workspace_service.create_enhancement_workspace(
                resume_id=resume_id,
                job_id=None,
                enhancement_type="invalid_type",
            )


class TestPathGetters:
    """Test path getter methods."""

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_get_resume_path(self, workspace_service):
        """Test getting resume directory path."""
        resume_id = "test-resume-id-123"
        path = workspace_service.get_resume_path(resume_id)

        assert path == workspace_service.workspace_root / "resumes" / "original" / resume_id

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_get_job_path(self, workspace_service):
        """Test getting job directory path."""
        job_id = "test-job-id-456"
        path = workspace_service.get_job_path(job_id)

        assert path == workspace_service.workspace_root / "jobs" / job_id

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_get_enhancement_path(self, workspace_service):
        """Test getting enhancement directory path."""
        enhancement_id = "test-enhancement-id-789"
        path = workspace_service.get_enhancement_path(enhancement_id)

        assert path == workspace_service.workspace_root / "resumes" / "enhanced" / enhancement_id


class TestEnhancementCompletion:
    """Test enhancement completion checking."""

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_check_enhancement_complete_true(self, workspace_service):
        """Test checking enhancement completion when enhanced.md exists."""
        resume_id = str(uuid4())
        job_id = str(uuid4())

        enhancement_id, enhancement_dir = workspace_service.create_enhancement_workspace(
            resume_id=resume_id,
            job_id=job_id,
            enhancement_type="job_tailoring",
        )

        # Create enhanced.md to simulate completion
        enhanced_file = enhancement_dir / "enhanced.md"
        enhanced_file.write_text("# Enhanced Resume\n\nContent here...")

        # Check completion
        is_complete = workspace_service.check_enhancement_complete(enhancement_id)
        assert is_complete is True

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_check_enhancement_complete_false(self, workspace_service):
        """Test checking enhancement completion when enhanced.md doesn't exist."""
        resume_id = str(uuid4())
        job_id = str(uuid4())

        enhancement_id, enhancement_dir = workspace_service.create_enhancement_workspace(
            resume_id=resume_id,
            job_id=job_id,
            enhancement_type="job_tailoring",
        )

        # Don't create enhanced.md

        # Check completion
        is_complete = workspace_service.check_enhancement_complete(enhancement_id)
        assert is_complete is False

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_list_pending_enhancements_empty(self, workspace_service):
        """Test listing pending enhancements when none exist."""
        pending = workspace_service.list_pending_enhancements()
        assert pending == []

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_list_pending_enhancements_with_pending(self, workspace_service):
        """Test listing pending enhancements with some pending."""
        resume_id = str(uuid4())
        job_id = str(uuid4())

        # Create pending enhancement
        enhancement_id_1, _ = workspace_service.create_enhancement_workspace(
            resume_id=resume_id,
            job_id=job_id,
            enhancement_type="job_tailoring",
        )

        # Create another pending enhancement
        enhancement_id_2, _ = workspace_service.create_enhancement_workspace(
            resume_id=resume_id,
            job_id=None,
            enhancement_type="industry_revamp",
            industry="Healthcare",
        )

        # List pending
        pending = workspace_service.list_pending_enhancements()

        assert len(pending) == 2

        # Verify both are in the list
        enhancement_ids = [e["enhancement_id"] for e in pending]
        assert enhancement_id_1 in enhancement_ids
        assert enhancement_id_2 in enhancement_ids

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_list_pending_enhancements_excludes_completed(self, workspace_service):
        """Test that completed enhancements are excluded from pending list."""
        resume_id = str(uuid4())
        job_id = str(uuid4())

        # Create pending enhancement
        enhancement_id_1, _ = workspace_service.create_enhancement_workspace(
            resume_id=resume_id,
            job_id=job_id,
            enhancement_type="job_tailoring",
        )

        # Create completed enhancement
        enhancement_id_2, enhancement_dir_2 = workspace_service.create_enhancement_workspace(
            resume_id=resume_id,
            job_id=job_id,
            enhancement_type="job_tailoring",
        )

        # Mark second as completed by creating enhanced.md
        enhanced_file = enhancement_dir_2 / "enhanced.md"
        enhanced_file.write_text("# Completed Resume")

        # List pending
        pending = workspace_service.list_pending_enhancements()

        # Should only have the first one
        assert len(pending) == 1
        assert pending[0]["enhancement_id"] == enhancement_id_1

    @pytest.mark.unit
    @pytest.mark.workspace
    def test_list_pending_enhancements_returns_metadata(self, workspace_service):
        """Test that pending list returns full metadata."""
        resume_id = str(uuid4())
        job_id = str(uuid4())

        enhancement_id, _ = workspace_service.create_enhancement_workspace(
            resume_id=resume_id,
            job_id=job_id,
            enhancement_type="job_tailoring",
        )

        pending = workspace_service.list_pending_enhancements()

        assert len(pending) == 1
        metadata = pending[0]

        # Verify metadata structure
        assert metadata["enhancement_id"] == enhancement_id
        assert metadata["resume_id"] == resume_id
        assert metadata["job_id"] == job_id
        assert metadata["enhancement_type"] == "job_tailoring"
        assert metadata["status"] == "pending"
        assert "created_at" in metadata
