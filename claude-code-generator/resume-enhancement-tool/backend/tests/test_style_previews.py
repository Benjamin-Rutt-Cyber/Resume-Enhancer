"""
Tests for style preview feature.

This module tests:
- Style preview generation via Anthropic API
- Style selection and persistence
- Style validation
- Integration with enhancement workflow
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from pathlib import Path

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models import Resume
from app.config.styles import STYLES, get_style_names, validate_style
from app.services.anthropic_service import AnthropicService


# ============================================================================
# Style Configuration Tests
# ============================================================================


def test_styles_config():
    """Test that all 5 styles are properly configured."""
    assert len(STYLES) == 5

    expected_styles = ["professional", "executive", "technical", "creative", "concise"]
    assert set(STYLES.keys()) == set(expected_styles)

    # Verify each style has required fields
    for style_key, style_config in STYLES.items():
        assert "name" in style_config
        assert "description" in style_config
        assert "tone" in style_config
        assert "prompt_guidance" in style_config


def test_get_style_names():
    """Test getting list of style names."""
    names = get_style_names()
    assert len(names) == 5
    assert "professional" in names
    assert "executive" in names
    assert "technical" in names
    assert "creative" in names
    assert "concise" in names


def test_validate_style():
    """Test style validation."""
    # Valid styles should pass
    assert validate_style("professional") is True
    assert validate_style("executive") is True
    assert validate_style("technical") is True
    assert validate_style("creative") is True
    assert validate_style("concise") is True

    # Invalid styles should fail
    assert validate_style("invalid") is False
    assert validate_style("") is False
    assert validate_style(None) is False


# ============================================================================
# API Endpoint Tests
# ============================================================================


@pytest.mark.asyncio
async def test_generate_style_previews(client: TestClient, test_db: Session, test_resume: Resume):
    """Test POST /api/resumes/{id}/style-previews generates all 5 previews."""
    # Mock AnthropicService to avoid real API calls
    mock_previews = {
        "professional": "Experienced software engineer with proven track record...",
        "executive": "Strategic technology leader driving innovation...",
        "technical": "Python/FastAPI developer specializing in microservices...",
        "creative": "Passionate engineer transforming ideas into reality...",
        "concise": "5+ years full-stack dev. Python, React, AWS expert.",
    }

    with patch("app.api.routes.style_previews.AnthropicService") as mock_service_class:
        # Setup mock
        mock_service = Mock()
        mock_service.generate_all_style_previews = AsyncMock(return_value=mock_previews)
        mock_service_class.return_value = mock_service

        # Make request
        response = client.post(f"/api/resumes/{test_resume.id}/style-previews")

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert data["resume_id"] == str(test_resume.id)
        assert len(data["previews"]) == 5

        # Verify all styles are present
        style_names = [p["style"] for p in data["previews"]]
        assert set(style_names) == set(get_style_names())

        # Verify preview structure
        for preview in data["previews"]:
            assert "style" in preview
            assert "name" in preview
            assert "description" in preview
            assert "preview_text" in preview

        # Verify style_previews_generated flag is set
        test_db.refresh(test_resume)
        assert test_resume.style_previews_generated is True


def test_get_style_previews(client: TestClient, test_resume: Resume, temp_workspace: Path):
    """Test GET /api/resumes/{id}/style-previews retrieves existing previews."""
    # Create preview files in workspace
    preview_dir = temp_workspace / "resumes" / "original" / str(test_resume.id) / "style_previews"
    preview_dir.mkdir(parents=True, exist_ok=True)

    previews_data = {
        "professional": "Professional preview text...",
        "executive": "Executive preview text...",
        "technical": "Technical preview text...",
        "creative": "Creative preview text...",
        "concise": "Concise preview.",
    }

    for style, text in previews_data.items():
        (preview_dir / f"{style}.txt").write_text(text)

    # Mock workspace service to use temp workspace
    with patch("app.api.routes.style_previews.WorkspaceService") as mock_ws_class:
        mock_ws = Mock()
        mock_ws.get_resume_path.return_value = temp_workspace / "resumes" / "original" / str(test_resume.id)
        mock_ws_class.return_value = mock_ws

        # Make request
        response = client.get(f"/api/resumes/{test_resume.id}/style-previews")

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert data["resume_id"] == str(test_resume.id)
        assert len(data["previews"]) == 5


def test_get_style_previews_not_found(client: TestClient, test_resume: Resume):
    """Test GET /api/resumes/{id}/style-previews returns 404 if not generated."""
    # Mock workspace service to return non-existent path
    with patch("app.api.routes.style_previews.WorkspaceService") as mock_ws_class:
        mock_ws = Mock()
        mock_ws.get_resume_path.return_value = Path("/nonexistent/path")
        mock_ws_class.return_value = mock_ws

        response = client.get(f"/api/resumes/{test_resume.id}/style-previews")
        assert response.status_code == 404


def test_select_style(client: TestClient, test_db: Session, test_resume: Resume):
    """Test POST /api/resumes/{id}/select-style saves style to database."""
    # Select professional style
    response = client.post(
        f"/api/resumes/{test_resume.id}/select-style",
        json={"style": "professional"}
    )

    # Assertions
    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Style selected successfully"
    assert data["selected_style"] == "professional"

    # Verify database update
    test_db.refresh(test_resume)
    assert test_resume.selected_style == "professional"


def test_select_invalid_style(client: TestClient, test_resume: Resume):
    """Test POST /api/resumes/{id}/select-style rejects invalid styles."""
    response = client.post(
        f"/api/resumes/{test_resume.id}/select-style",
        json={"style": "invalid_style"}
    )

    assert response.status_code == 400
    assert "Invalid style" in response.json()["detail"]


def test_select_style_resume_not_found(client: TestClient):
    """Test POST /api/resumes/{id}/select-style returns 404 for non-existent resume."""
    fake_id = str(uuid4())
    response = client.post(
        f"/api/resumes/{fake_id}/select-style",
        json={"style": "professional"}
    )

    assert response.status_code == 404


# ============================================================================
# Anthropic Service Tests
# ============================================================================


@pytest.mark.asyncio
async def test_anthropic_service_generate_single_preview():
    """Test AnthropicService generates a single style preview."""
    # Mock Anthropic client
    with patch("app.services.anthropic_service.Anthropic") as mock_anthropic_class:
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text="This is a professional summary preview.")]
        mock_client.messages.create = AsyncMock(return_value=mock_message)
        mock_anthropic_class.return_value = mock_client

        # Create service
        service = AnthropicService(api_key="test-key", workspace_root=Path("/tmp"))

        # Generate preview
        preview_text = await service.generate_style_preview(
            resume_text="John Doe Software Engineer...",
            style="professional"
        )

        # Assertions
        assert preview_text == "This is a professional summary preview."
        assert mock_client.messages.create.called


@pytest.mark.asyncio
async def test_anthropic_service_generate_all_previews():
    """Test AnthropicService generates all 5 previews in parallel."""
    with patch("app.services.anthropic_service.Anthropic") as mock_anthropic_class:
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text="Preview text")]
        mock_client.messages.create = AsyncMock(return_value=mock_message)
        mock_anthropic_class.return_value = mock_client

        service = AnthropicService(api_key="test-key", workspace_root=Path("/tmp"))

        previews = await service.generate_all_style_previews(
            resume_text="John Doe Software Engineer..."
        )

        # Should return dict with 5 styles
        assert len(previews) == 5
        assert all(style in previews for style in get_style_names())

        # Should have called API 5 times (once per style)
        assert mock_client.messages.create.call_count == 5


# ============================================================================
# Integration with Enhancement Workflow
# ============================================================================


def test_style_passed_to_enhancement(
    client: TestClient,
    test_db: Session,
    test_resume: Resume,
    test_job
):
    """Test that selected style is passed to enhancement INSTRUCTIONS.md."""
    # Set resume style
    test_resume.selected_style = "technical"
    test_db.commit()

    # Mock workspace service to capture INSTRUCTIONS.md content
    instructions_content = None

    def mock_create_enhancement_workspace(
        resume_id, job_id, enhancement_type, industry=None, style=None
    ):
        nonlocal instructions_content

        # Simulate real workspace service behavior
        from app.services.workspace_service import WorkspaceService

        ws = WorkspaceService(Path("/tmp"))
        instructions_content = ws._create_instructions(
            enhancement_id="test-123",
            resume_id=resume_id,
            job_id=job_id,
            enhancement_type=enhancement_type,
            industry=industry,
            style=style
        )

        return "test-enhancement-id", Path("/tmp/test")

    with patch("app.api.routes.enhancements.workspace_service") as mock_ws:
        mock_ws.create_enhancement_workspace = mock_create_enhancement_workspace

        # Create enhancement
        response = client.post(
            "/api/enhancements/tailor",
            json={
                "resume_id": str(test_resume.id),
                "job_id": str(test_job.id),
                "enhancement_type": "job_tailoring"
            }
        )

        # Check that INSTRUCTIONS.md includes style guidance
        assert instructions_content is not None
        assert "Style Guidelines" in instructions_content
        assert "Technical" in instructions_content  # Style name
        assert "technical, precise, detailed" in instructions_content  # Style tone


def test_enhancement_without_style_works(
    client: TestClient,
    test_db: Session,
    test_resume: Resume,
    test_job
):
    """Test that enhancement works when no style is selected (backward compatibility)."""
    # Don't set any style on resume
    assert test_resume.selected_style is None

    # Mock workspace service
    with patch("app.api.routes.enhancements.workspace_service") as mock_ws:
        mock_ws.create_enhancement_workspace.return_value = (
            "test-enhancement-id",
            Path("/tmp/test")
        )

        # Create enhancement
        response = client.post(
            "/api/enhancements/tailor",
            json={
                "resume_id": str(test_resume.id),
                "job_id": str(test_job.id),
                "enhancement_type": "job_tailoring"
            }
        )

        # Should still work
        assert response.status_code in [200, 201]

        # Verify style=None was passed
        call_args = mock_ws.create_enhancement_workspace.call_args
        assert call_args.kwargs.get("style") is None


# ============================================================================
# Database Model Tests
# ============================================================================


def test_resume_model_style_fields(test_db: Session):
    """Test Resume model has style-related fields."""
    resume = Resume(
        id=uuid4(),
        filename="test.pdf",
        original_format="pdf",
        file_path="/test/path",
        extracted_text_path="/test/extracted.txt",
        file_size_bytes=1000,
        word_count=100,
        selected_style="executive",
        style_previews_generated=True
    )

    test_db.add(resume)
    test_db.commit()
    test_db.refresh(resume)

    assert resume.selected_style == "executive"
    assert resume.style_previews_generated is True


def test_resume_style_defaults(test_db: Session):
    """Test Resume model style fields have correct defaults."""
    resume = Resume(
        id=uuid4(),
        filename="test.pdf",
        original_format="pdf",
        file_path="/test/path",
        extracted_text_path="/test/extracted.txt",
        file_size_bytes=1000,
        word_count=100
    )

    test_db.add(resume)
    test_db.commit()
    test_db.refresh(resume)

    assert resume.selected_style is None
    assert resume.style_previews_generated is False


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.asyncio
async def test_anthropic_api_error_handling():
    """Test AnthropicService handles API errors gracefully."""
    with patch("app.services.anthropic_service.Anthropic") as mock_anthropic_class:
        mock_client = Mock()
        mock_client.messages.create = AsyncMock(side_effect=Exception("API Error"))
        mock_anthropic_class.return_value = mock_client

        service = AnthropicService(api_key="test-key", workspace_root=Path("/tmp"))

        # Should raise exception
        with pytest.raises(Exception):
            await service.generate_style_preview(
                resume_text="Test text",
                style="professional"
            )


def test_generate_previews_resume_not_found(client: TestClient):
    """Test generating previews for non-existent resume returns 404."""
    fake_id = str(uuid4())
    response = client.post(f"/api/resumes/{fake_id}/style-previews")
    assert response.status_code == 404
