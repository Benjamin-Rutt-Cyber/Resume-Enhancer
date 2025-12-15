"""
Tests for Resume API endpoints.

This module tests the resume upload and management API, including:
- POST /api/resumes/upload - File upload with validation
- GET /api/resumes - List resumes with pagination
- GET /api/resumes/{id} - Retrieve specific resume
"""

import io
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from tests.utils import (
    create_test_pdf,
    create_test_docx,
    create_empty_pdf,
    SAMPLE_RESUME_SHORT,
    SAMPLE_RESUME_VALID,
    SAMPLE_RESUME_LONG,
)


class TestResumeUpload:
    """Test suite for POST /api/resumes/upload endpoint."""

    @pytest.mark.api
    def test_upload_resume_pdf_success(self, client, tmp_path, temp_workspace):
        """Test successful PDF resume upload."""
        # Create test PDF
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "test.pdf")

        # Upload the PDF
        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/resumes/upload",
                files={"file": ("test_resume.pdf", f, "application/pdf")}
            )

        # Verify successful upload
        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert data["filename"] == "test_resume.pdf"
        assert data["original_format"] == "pdf"
        assert data["word_count"] >= 50
        assert data["file_size_bytes"] > 0

    @pytest.mark.api
    def test_upload_resume_docx_success(self, client, tmp_path, temp_workspace):
        """Test successful DOCX resume upload."""
        # Create test DOCX
        docx_path = create_test_docx(SAMPLE_RESUME_VALID, tmp_path / "test.docx")

        # Upload the DOCX
        with open(docx_path, "rb") as f:
            response = client.post(
                "/api/resumes/upload",
                files={"file": ("test_resume.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            )

        # Verify successful upload
        assert response.status_code == 201
        data = response.json()

        assert data["filename"] == "test_resume.docx"
        assert data["original_format"] == "docx"
        assert data["word_count"] >= 50

    @pytest.mark.api
    def test_upload_resume_invalid_format(self, client, tmp_path):
        """Test rejection of invalid file formats."""
        # Create a text file
        txt_file = tmp_path / "resume.txt"
        txt_file.write_text(SAMPLE_RESUME_VALID)

        # Try to upload text file
        with open(txt_file, "rb") as f:
            response = client.post(
                "/api/resumes/upload",
                files={"file": ("resume.txt", f, "text/plain")}
            )

        # Should reject with 400
        assert response.status_code == 400
        assert "Unsupported file format" in response.json()["detail"]

    @pytest.mark.api
    def test_upload_resume_too_short(self, client, tmp_path):
        """
        Test rejection of resumes with < 50 words.

        This test VERIFIES THE BUG FIX: Previously accepted resumes with only 1 word.
        Now correctly rejects resumes with < 50 words.
        """
        # Create PDF with very short content (< 50 words)
        pdf_path = create_test_pdf(SAMPLE_RESUME_SHORT, tmp_path / "short.pdf")

        # Try to upload short resume
        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/resumes/upload",
                files={"file": ("short_resume.pdf", f, "application/pdf")}
            )

        # Should reject with 400 (bug fix verification!)
        assert response.status_code == 400
        assert "too short" in response.json()["detail"].lower()
        assert "50 words" in response.json()["detail"]

    @pytest.mark.api
    def test_upload_resume_empty_file(self, client, tmp_path):
        """Test rejection of empty files."""
        # Create empty PDF
        pdf_path = create_empty_pdf(tmp_path / "empty.pdf")

        # Try to upload empty file
        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/resumes/upload",
                files={"file": ("empty.pdf", f, "application/pdf")}
            )

        # Should reject with 400
        assert response.status_code == 400
        detail = response.json()["detail"].lower()
        assert "empty" in detail or "no text" in detail

    @pytest.mark.api
    def test_upload_resume_file_too_large(self, client):
        """Test rejection of files exceeding size limit (10 MB)."""
        # Create a file larger than MAX_FILE_SIZE (10 MB)
        large_content = b"x" * (11 * 1024 * 1024)  # 11 MB

        # Try to upload large file
        response = client.post(
            "/api/resumes/upload",
            files={"file": ("large_resume.pdf", io.BytesIO(large_content), "application/pdf")}
        )

        # Should reject with 413
        assert response.status_code == 413
        assert "too large" in response.json()["detail"].lower()
        assert "10 MB" in response.json()["detail"]

    @pytest.mark.api
    def test_upload_resume_no_filename(self, client):
        """Test rejection when filename is missing."""
        # Create file upload without filename
        response = client.post(
            "/api/resumes/upload",
            files={"file": ("", b"content", "application/pdf")}
        )

        # FastAPI returns 422 for validation errors
        assert response.status_code == 422
        # Verify it's a validation error
        assert "detail" in response.json()

    @pytest.mark.api
    def test_upload_resume_long_valid(self, client, tmp_path):
        """Test uploading a long but valid resume."""
        # Create PDF with long content
        pdf_path = create_test_pdf(SAMPLE_RESUME_LONG, tmp_path / "long.pdf")

        # Upload the PDF
        with open(pdf_path, "rb") as f:
            response = client.post(
                "/api/resumes/upload",
                files={"file": ("long_resume.pdf", f, "application/pdf")}
            )

        # Should succeed
        assert response.status_code == 201
        data = response.json()
        assert data["word_count"] > 100


class TestResumeList:
    """Test suite for GET /api/resumes endpoint."""

    @pytest.mark.api
    def test_list_resumes_empty(self, client):
        """Test listing resumes when none exist."""
        response = client.get("/api/resumes")

        assert response.status_code == 200
        data = response.json()

        assert "resumes" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["resumes"]) == 0

    @pytest.mark.api
    def test_list_resumes_with_data(self, client, test_resume):
        """Test listing resumes when some exist."""
        response = client.get("/api/resumes")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] >= 1
        assert len(data["resumes"]) >= 1

        # Verify resume structure
        resume = data["resumes"][0]
        assert "id" in resume
        assert "filename" in resume
        assert "created_at" in resume

    @pytest.mark.api
    def test_list_resumes_pagination(self, client, test_db):
        """Test resume listing with pagination."""
        from tests.utils import create_test_resume_in_db

        # Create multiple resumes
        for i in range(5):
            create_test_resume_in_db(
                test_db,
                filename=f"resume_{i}.pdf",
                word_count=100 + i
            )

        # Test skip parameter
        response = client.get("/api/resumes?skip=2&limit=2")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 5
        assert len(data["resumes"]) == 2

        # Test limit parameter
        response = client.get("/api/resumes?limit=3")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 5
        assert len(data["resumes"]) == 3


class TestResumeGet:
    """Test suite for GET /api/resumes/{id} endpoint."""

    @pytest.mark.api
    def test_get_resume_success(self, client, test_resume):
        """Test retrieving a specific resume by ID."""
        response = client.get(f"/api/resumes/{test_resume.id}")

        assert response.status_code == 200
        data = response.json()

        # Verify response matches the test resume
        assert data["id"] == str(test_resume.id)
        assert data["filename"] == test_resume.filename
        assert data["word_count"] == test_resume.word_count

    @pytest.mark.api
    def test_get_resume_not_found(self, client):
        """Test 404 response for non-existent resume."""
        # Generate a random UUID that doesn't exist
        fake_id = uuid4()

        response = client.get(f"/api/resumes/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.api
    def test_get_resume_invalid_uuid(self, client):
        """Test error handling for invalid UUID format."""
        response = client.get("/api/resumes/not-a-valid-uuid")

        # FastAPI should return 422 for invalid UUID format
        assert response.status_code == 422
