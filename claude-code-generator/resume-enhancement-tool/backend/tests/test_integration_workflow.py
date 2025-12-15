"""
Integration tests for complete workflows.

This module tests end-to-end workflows including:
- Complete job tailoring workflow (upload → job → enhance → download)
- Complete industry revamp workflow (upload → revamp → download)
- Error handling and rollback scenarios
- Multiple enhancements for same resume
"""

import json
import pytest
from pathlib import Path
from uuid import UUID

from tests.utils import (
    create_test_pdf,
    create_test_docx,
    SAMPLE_RESUME_VALID,
    SAMPLE_JOB_DESCRIPTION,
)


class TestJobTailoringWorkflow:
    """Test complete job tailoring workflow."""

    @pytest.mark.integration
    def test_complete_job_tailoring_workflow(self, client, tmp_path):
        """
        Test complete workflow: Upload resume → Create job → Create enhancement → Check status.

        This integration test verifies the entire user workflow works end-to-end.
        """
        # Step 1: Upload a resume
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "resume.pdf")

        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/resumes/upload",
                files={"file": ("test_resume.pdf", f, "application/pdf")}
            )

        assert response.status_code == 201
        resume_data = response.json()
        resume_id = resume_data["id"]

        # Step 2: Create a job description
        job_payload = {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "description_text": SAMPLE_JOB_DESCRIPTION,
            "source": "company_website",
        }

        response = client.post("/api/jobs", json=job_payload)
        assert response.status_code == 201
        job_data = response.json()
        job_id = job_data["id"]

        # Step 3: Create enhancement request
        enhancement_payload = {
            "resume_id": resume_id,
            "job_id": job_id,
            "enhancement_type": "job_tailoring",
        }

        response = client.post("/api/enhancements/tailor", json=enhancement_payload)
        assert response.status_code == 201
        enhancement_data = response.json()
        enhancement_id = enhancement_data["id"]

        # Verify enhancement was created
        assert enhancement_data["resume_id"] == resume_id
        assert enhancement_data["job_id"] == job_id
        assert enhancement_data["enhancement_type"] == "job_tailoring"
        assert enhancement_data["status"] == "pending"

        # Step 4: List enhancements for the resume
        response = client.get(f"/api/enhancements?resume_id={resume_id}")
        assert response.status_code == 200

        enhancements_list = response.json()
        assert "enhancements" in enhancements_list
        assert len(enhancements_list["enhancements"]) >= 1

        # Step 5: Get specific enhancement
        response = client.get(f"/api/enhancements/{enhancement_id}")
        assert response.status_code == 200

        enhancement_details = response.json()
        assert enhancement_details["id"] == enhancement_id
        assert enhancement_details["status"] == "pending"

    @pytest.mark.integration
    def test_multiple_enhancements_same_resume(self, client, tmp_path):
        """Test creating multiple enhancements for the same resume."""
        # Upload resume
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "resume.pdf")

        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/resumes/upload",
                files={"file": ("resume.pdf", f, "application/pdf")}
            )

        resume_id = response.json()["id"]

        # Create two different jobs
        job1 = client.post("/api/jobs", json={
            "title": "Software Engineer",
            "company": "Company A",
            "description_text": "Looking for a software engineer with Python experience.",
        }).json()

        job2 = client.post("/api/jobs", json={
            "title": "DevOps Engineer",
            "company": "Company B",
            "description_text": "Seeking a DevOps engineer with AWS and Docker expertise.",
        }).json()

        # Create two enhancements for the same resume
        enhancement1 = client.post("/api/enhancements/tailor", json={
            "resume_id": resume_id,
            "job_id": job1["id"],
            "enhancement_type": "job_tailoring",
        }).json()

        enhancement2 = client.post("/api/enhancements/tailor", json={
            "resume_id": resume_id,
            "job_id": job2["id"],
            "enhancement_type": "job_tailoring",
        }).json()

        # Verify both enhancements exist
        assert enhancement1["id"] != enhancement2["id"]
        assert enhancement1["resume_id"] == resume_id
        assert enhancement2["resume_id"] == resume_id

        # List enhancements
        response = client.get(f"/api/enhancements?resume_id={resume_id}")
        enhancements = response.json()["enhancements"]

        assert len(enhancements) == 2


class TestIndustryRevampWorkflow:
    """Test complete industry revamp workflow."""

    @pytest.mark.integration
    def test_complete_industry_revamp_workflow(self, client, tmp_path):
        """
        Test complete workflow: Upload resume → Create industry revamp → Check status.
        """
        # Step 1: Upload a resume
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "resume.pdf")

        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/resumes/upload",
                files={"file": ("resume.pdf", f, "application/pdf")}
            )

        resume_id = response.json()["id"]

        # Step 2: Create industry revamp enhancement
        enhancement_payload = {
            "resume_id": resume_id,
            "industry": "IT",
        }

        response = client.post("/api/enhancements/revamp", json=enhancement_payload)
        assert response.status_code == 201

        enhancement_data = response.json()
        enhancement_id = enhancement_data["id"]

        # Verify enhancement details
        assert enhancement_data["resume_id"] == resume_id
        assert enhancement_data["enhancement_type"] == "industry_revamp"
        assert enhancement_data["industry"] == "IT"
        assert enhancement_data["status"] == "pending"
        assert enhancement_data["job_id"] is None

        # Step 3: Get enhancement details
        response = client.get(f"/api/enhancements/{enhancement_id}")
        assert response.status_code == 200

        details = response.json()
        assert details["industry"] == "IT"

    @pytest.mark.integration
    def test_revamp_and_tailor_same_resume(self, client, tmp_path):
        """Test creating both revamp and tailor enhancements for same resume."""
        # Upload resume
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "resume.pdf")

        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/resumes/upload",
                files={"file": ("resume.pdf", f, "application/pdf")}
            )

        resume_id = response.json()["id"]

        # Create job
        job = client.post("/api/jobs", json={
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description_text": SAMPLE_JOB_DESCRIPTION,
        }).json()

        # Create industry revamp
        revamp = client.post("/api/enhancements/revamp", json={
            "resume_id": resume_id,
            "industry": "Cybersecurity",
        }).json()

        # Create job tailoring
        tailor = client.post("/api/enhancements/tailor", json={
            "resume_id": resume_id,
            "job_id": job["id"],
            "enhancement_type": "job_tailoring",
        }).json()

        # Verify both exist
        assert revamp["enhancement_type"] == "industry_revamp"
        assert tailor["enhancement_type"] == "job_tailoring"

        # List all enhancements
        response = client.get(f"/api/enhancements?resume_id={resume_id}")
        enhancements = response.json()["enhancements"]

        assert len(enhancements) == 2


class TestErrorHandling:
    """Test error handling and validation in workflows."""

    @pytest.mark.integration
    def test_tailor_with_invalid_resume_id(self, client):
        """Test that tailoring with non-existent resume returns 404."""
        from uuid import uuid4

        # Create valid job
        job = client.post("/api/jobs", json={
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description_text": SAMPLE_JOB_DESCRIPTION,
        }).json()

        # Try to create enhancement with fake resume ID
        fake_resume_id = str(uuid4())

        response = client.post("/api/enhancements/tailor", json={
            "resume_id": fake_resume_id,
            "job_id": job["id"],
            "enhancement_type": "job_tailoring",
        })

        assert response.status_code == 404
        assert "Resume not found" in response.json()["detail"]

    @pytest.mark.integration
    def test_tailor_with_invalid_job_id(self, client, tmp_path):
        """Test that tailoring with non-existent job returns 404."""
        from uuid import uuid4

        # Create valid resume
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "resume.pdf")

        with open(pdf_path, "rb") as f:
            resume = client.post(
                "/api/resumes/upload",
                files={"file": ("resume.pdf", f, "application/pdf")}
            ).json()

        # Try to create enhancement with fake job ID
        fake_job_id = str(uuid4())

        response = client.post("/api/enhancements/tailor", json={
            "resume_id": resume["id"],
            "job_id": fake_job_id,
            "enhancement_type": "job_tailoring",
        })

        assert response.status_code == 404
        assert "Job not found" in response.json()["detail"]

    @pytest.mark.integration
    def test_revamp_with_invalid_resume_id(self, client):
        """Test that revamp with non-existent resume returns 404."""
        from uuid import uuid4

        fake_resume_id = str(uuid4())

        response = client.post("/api/enhancements/revamp", json={
            "resume_id": fake_resume_id,
            "industry": "IT",
        })

        assert response.status_code == 404
        assert "Resume not found" in response.json()["detail"]

    @pytest.mark.integration
    def test_get_nonexistent_enhancement(self, client):
        """Test getting enhancement that doesn't exist returns 404."""
        from uuid import uuid4

        fake_id = str(uuid4())

        response = client.get(f"/api/enhancements/{fake_id}")

        assert response.status_code == 404
        assert "Enhancement not found" in response.json()["detail"]

    @pytest.mark.integration
    def test_invalid_resume_upload_doesnt_create_record(self, client, test_db, tmp_path):
        """Test that invalid resume upload doesn't create database record."""
        from app.models import Resume

        # Count resumes before
        resumes_before = test_db.query(Resume).count()

        # Try to upload invalid file (too short)
        from tests.utils import SAMPLE_RESUME_SHORT, create_test_pdf

        pdf_path = create_test_pdf(SAMPLE_RESUME_SHORT, tmp_path / "short.pdf")

        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/resumes/upload",
                files={"file": ("short.pdf", f, "application/pdf")}
            )

        # Should fail validation
        assert response.status_code == 400

        # Count resumes after
        resumes_after = test_db.query(Resume).count()

        # No new resume should be created
        assert resumes_after == resumes_before


class TestDatabaseConsistency:
    """Test database integrity and foreign key relationships."""

    @pytest.mark.integration
    @pytest.mark.database
    def test_enhancement_has_valid_foreign_keys(self, client, tmp_path):
        """Test that enhancement properly links to resume and job."""
        # Create resume
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "resume.pdf")

        with open(pdf_path, "rb") as f:
            resume = client.post(
                "/api/resumes/upload",
                files={"file": ("resume.pdf", f, "application/pdf")}
            ).json()

        # Create job
        job = client.post("/api/jobs", json={
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description_text": SAMPLE_JOB_DESCRIPTION,
        }).json()

        # Create enhancement
        enhancement = client.post("/api/enhancements/tailor", json={
            "resume_id": resume["id"],
            "job_id": job["id"],
            "enhancement_type": "job_tailoring",
        }).json()

        # Verify we can retrieve the resume
        resume_response = client.get(f"/api/resumes/{resume['id']}")
        assert resume_response.status_code == 200

        # Verify we can retrieve the job
        job_response = client.get(f"/api/jobs/{job['id']}")
        assert job_response.status_code == 200

        # Verify we can retrieve the enhancement
        enhancement_response = client.get(f"/api/enhancements/{enhancement['id']}")
        assert enhancement_response.status_code == 200

        # Verify foreign keys match
        enhancement_data = enhancement_response.json()
        assert enhancement_data["resume_id"] == resume["id"]
        assert enhancement_data["job_id"] == job["id"]

    @pytest.mark.integration
    @pytest.mark.database
    def test_list_enhancements_by_resume(self, client, tmp_path):
        """Test listing enhancements filtered by resume ID."""
        # Create two resumes
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "resume1.pdf")

        with open(pdf_path, "rb") as f:
            resume1 = client.post(
                "/api/resumes/upload",
                files={"file": ("resume1.pdf", f, "application/pdf")}
            ).json()

        with open(pdf_path, "rb") as f:
            resume2 = client.post(
                "/api/resumes/upload",
                files={"file": ("resume2.pdf", f, "application/pdf")}
            ).json()

        # Create job
        job = client.post("/api/jobs", json={
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description_text": SAMPLE_JOB_DESCRIPTION,
        }).json()

        # Create enhancement for resume1
        client.post("/api/enhancements/tailor", json={
            "resume_id": resume1["id"],
            "job_id": job["id"],
            "enhancement_type": "job_tailoring",
        })

        # Create enhancement for resume2
        client.post("/api/enhancements/tailor", json={
            "resume_id": resume2["id"],
            "job_id": job["id"],
            "enhancement_type": "job_tailoring",
        })

        # List all enhancements
        response = client.get("/api/enhancements")
        all_enhancements = response.json()["enhancements"]

        # Should have 2 total enhancements
        assert len(all_enhancements) == 2

        # Filter for resume1's enhancements
        resume1_enhancements = [e for e in all_enhancements if e["resume_id"] == resume1["id"]]
        resume2_enhancements = [e for e in all_enhancements if e["resume_id"] == resume2["id"]]

        # Should only have 1 enhancement each
        assert len(resume1_enhancements) == 1
        assert len(resume2_enhancements) == 1
        assert resume1_enhancements[0]["resume_id"] == resume1["id"]
        assert resume2_enhancements[0]["resume_id"] == resume2["id"]


class TestFileOperations:
    """Test file operations in workflows."""

    @pytest.mark.integration
    def test_docx_upload_and_enhance_workflow(self, client, tmp_path):
        """Test complete workflow with DOCX file instead of PDF."""
        from tests.utils import create_test_docx

        # Upload DOCX
        docx_path = create_test_docx(SAMPLE_RESUME_VALID, tmp_path / "resume.docx")

        with open(docx_path, "rb") as f:
            resume = client.post(
                "/api/resumes/upload",
                files={"file": ("resume.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            ).json()

        # Create job
        job = client.post("/api/jobs", json={
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description_text": SAMPLE_JOB_DESCRIPTION,
        }).json()

        # Create enhancement
        enhancement = client.post("/api/enhancements/tailor", json={
            "resume_id": resume["id"],
            "job_id": job["id"],
            "enhancement_type": "job_tailoring",
        }).json()

        # Verify all worked
        assert resume["original_format"] == "docx"
        assert enhancement["enhancement_type"] == "job_tailoring"

    @pytest.mark.integration
    def test_long_resume_workflow(self, client, tmp_path):
        """Test workflow with very long resume."""
        from tests.utils import SAMPLE_RESUME_LONG, create_test_pdf

        # Upload long resume
        pdf_path = create_test_pdf(SAMPLE_RESUME_LONG, tmp_path / "long_resume.pdf")

        with open(pdf_path, "rb") as f:
            resume = client.post(
                "/api/resumes/upload",
                files={"file": ("long_resume.pdf", f, "application/pdf")}
            ).json()

        # Verify long resume was accepted
        assert resume["word_count"] > 100

        # Create enhancement
        job = client.post("/api/jobs", json={
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description_text": SAMPLE_JOB_DESCRIPTION,
        }).json()

        enhancement = client.post("/api/enhancements/tailor", json={
            "resume_id": resume["id"],
            "job_id": job["id"],
            "enhancement_type": "job_tailoring",
        }).json()

        assert enhancement["status"] == "pending"
