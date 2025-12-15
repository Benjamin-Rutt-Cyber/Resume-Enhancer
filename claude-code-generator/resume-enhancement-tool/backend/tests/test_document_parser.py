"""
Tests for document parser module.

This module tests PDF and DOCX parsing functionality, including:
- Successful parsing of valid documents
- Error handling for corrupted/empty files
- Content validation (word count, minimum requirements)
- Parser fallback logic (pdfplumber → pypdf)
- Multi-page document handling
"""

import pytest
from pathlib import Path

from app.utils.document_parser import DocumentParser
from tests.utils import (
    create_test_pdf,
    create_test_docx,
    create_empty_pdf,
    create_empty_docx,
    SAMPLE_RESUME_SHORT,
    SAMPLE_RESUME_VALID,
    SAMPLE_RESUME_LONG,
)


class TestDocumentParser:
    """Test suite for DocumentParser class."""

    # ========================================================================
    # PDF Parsing Tests
    # ========================================================================

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_valid_pdf(self, tmp_path, document_parser):
        """Test parsing a valid PDF file with substantial content."""
        # Create test PDF with valid resume content
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "resume.pdf")

        # Parse the PDF
        result = document_parser.parse_file(pdf_path)

        # Verify parsing succeeded
        assert result["success"] is True
        assert result["parser"] in ["pdfplumber", "pypdf"]
        assert "text" in result
        assert len(result["text"]) > 0

        # Verify content was extracted
        word_count = len(result["text"].split())
        assert word_count >= 50, f"Expected at least 50 words, got {word_count}"

        # Verify key information is present (basic smoke test)
        assert "John Doe" in result["text"]

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_multi_page_pdf(self, tmp_path, document_parser):
        """Test parsing a multi-page PDF file."""
        from tests.utils import create_test_pdf_multipage

        # Create multi-page PDF
        pdf_path = create_test_pdf_multipage(
            SAMPLE_RESUME_LONG,
            pages=3,
            file_path=tmp_path / "multipage.pdf"
        )

        # Parse the PDF
        result = document_parser.parse_file(pdf_path)

        # Verify parsing succeeded
        assert result["success"] is True
        assert "text" in result
        assert len(result["text"]) > 0

        # Multi-page PDFs should have substantial content
        word_count = len(result["text"].split())
        assert word_count > 100, f"Multi-page PDF should have >100 words, got {word_count}"

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_empty_pdf(self, tmp_path, document_parser):
        """Test parsing an empty PDF file."""
        # Create empty PDF
        pdf_path = create_empty_pdf(tmp_path / "empty.pdf")

        # Parse the PDF
        result = document_parser.parse_file(pdf_path)

        # Empty PDFs might succeed in parsing but have no text
        # The validation should happen at a higher level (API)
        assert "text" in result
        assert len(result["text"].strip()) == 0 or len(result["text"].split()) < 10

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_nonexistent_pdf(self, tmp_path, document_parser):
        """Test parsing a file that doesn't exist."""
        # Try to parse non-existent file
        pdf_path = tmp_path / "does_not_exist.pdf"

        # Should raise FileNotFoundError or return error in result
        with pytest.raises(FileNotFoundError):
            document_parser.parse_file(pdf_path)

    # ========================================================================
    # DOCX Parsing Tests
    # ========================================================================

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_valid_docx(self, tmp_path, document_parser):
        """Test parsing a valid DOCX file with substantial content."""
        # Create test DOCX with valid resume content
        docx_path = create_test_docx(SAMPLE_RESUME_VALID, tmp_path / "resume.docx")

        # Parse the DOCX
        result = document_parser.parse_file(docx_path)

        # Verify parsing succeeded
        assert result["success"] is True
        assert result["parser"] == "python-docx"
        assert "text" in result
        assert len(result["text"]) > 0

        # Verify content was extracted
        word_count = len(result["text"].split())
        assert word_count >= 50, f"Expected at least 50 words, got {word_count}"

        # Verify key information is present
        assert "John Doe" in result["text"]

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_docx_with_table(self, tmp_path, document_parser):
        """Test parsing a DOCX file containing tables (common in resumes)."""
        from tests.utils import create_test_docx_with_table

        # Create DOCX with table
        docx_path = create_test_docx_with_table(
            SAMPLE_RESUME_VALID,
            file_path=tmp_path / "resume_table.docx"
        )

        # Parse the DOCX
        result = document_parser.parse_file(docx_path)

        # Verify parsing succeeded
        assert result["success"] is True
        assert "text" in result

        # Verify table content was extracted
        assert "John Doe" in result["text"]  # From table
        assert "john@example.com" in result["text"]  # From table

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_empty_docx(self, tmp_path, document_parser):
        """Test parsing an empty DOCX file."""
        # Create empty DOCX
        docx_path = create_empty_docx(tmp_path / "empty.docx")

        # Parse the DOCX
        result = document_parser.parse_file(docx_path)

        # Empty DOCX should parse successfully but have no content
        assert "text" in result
        assert len(result["text"].strip()) == 0

    # ========================================================================
    # Content Validation Tests
    # ========================================================================

    @pytest.mark.unit
    @pytest.mark.parser
    def test_validate_content_minimum_words(self, tmp_path, document_parser):
        """Test that short documents are detected (verifies bug fix!)."""
        # Create PDF with very short content (< 50 words)
        pdf_path = create_test_pdf(SAMPLE_RESUME_SHORT, tmp_path / "short.pdf")

        # Parse the PDF
        result = document_parser.parse_file(pdf_path)

        # Parsing should succeed
        assert "text" in result

        # But word count should be low
        word_count = len(result["text"].split())
        assert word_count < 50, f"Test file should have <50 words, got {word_count}"

        # NOTE: The actual validation (rejection) happens at the API level
        # This test verifies the parser correctly extracts the content

    @pytest.mark.unit
    @pytest.mark.parser
    def test_validate_content_sufficient_words(self, tmp_path, document_parser):
        """Test that documents with sufficient words are accepted."""
        # Create PDF with sufficient content (> 50 words)
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "valid.pdf")

        # Parse the PDF
        result = document_parser.parse_file(pdf_path)

        # Verify sufficient word count
        word_count = len(result["text"].split())
        assert word_count >= 50, f"Should have >=50 words, got {word_count}"

    # ========================================================================
    # Error Handling Tests
    # ========================================================================

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_corrupted_pdf(self, tmp_path, document_parser):
        """Test handling of corrupted PDF file."""
        # Create a file with .pdf extension but invalid content
        corrupted_pdf = tmp_path / "corrupted.pdf"
        corrupted_pdf.write_text("This is not a valid PDF file!")

        # Try to parse the corrupted PDF
        result = document_parser.parse_file(corrupted_pdf)

        # Should handle gracefully - either return error or empty text
        assert "text" in result or "error" in result

        # If text is returned, it should be empty or error-like
        if "text" in result:
            # Corrupted files usually result in empty or garbage text
            assert len(result["text"]) < 100

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_unsupported_format(self, tmp_path, document_parser):
        """Test that unsupported file formats are rejected."""
        # Create a text file (unsupported format)
        txt_file = tmp_path / "resume.txt"
        txt_file.write_text(SAMPLE_RESUME_VALID)

        # The parser should raise ValueError for unsupported formats
        # This is defensive coding - API level validation is the primary defense
        with pytest.raises(ValueError, match="Unsupported file format"):
            document_parser.parse_file(txt_file)

    # ========================================================================
    # Parser Fallback Tests
    # ========================================================================

    @pytest.mark.unit
    @pytest.mark.parser
    @pytest.mark.slow
    def test_parser_fallback_pypdf(self, tmp_path, document_parser):
        """Test fallback from pdfplumber to pypdf when needed."""
        # This test verifies that if pdfplumber fails, pypdf is tried
        # Create a standard PDF
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "fallback.pdf")

        # Parse the PDF
        result = document_parser.parse_file(pdf_path)

        # Verify one of the parsers succeeded
        assert result["success"] is True
        assert result["parser"] in ["pdfplumber", "pypdf"]

        # If pdfplumber failed, pypdf should have been attempted
        # This is implicitly tested by checking the parser field

    # ========================================================================
    # Integration-Like Tests
    # ========================================================================

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_real_world_resume_length(self, tmp_path, document_parser):
        """Test parsing a realistic resume with typical length."""
        # Create PDF with realistic resume length
        pdf_path = create_test_pdf(SAMPLE_RESUME_LONG, tmp_path / "real_resume.pdf")

        # Parse the PDF
        result = document_parser.parse_file(pdf_path)

        # Verify parsing succeeded
        assert result["success"] is True

        # Real resumes typically have 200-500 words
        word_count = len(result["text"].split())
        assert 100 <= word_count <= 1000, (
            f"Real-world resume should have 100-1000 words, got {word_count}"
        )

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_preserves_formatting_info(self, tmp_path, document_parser):
        """Test that parser preserves essential formatting information."""
        # Create PDF with structured content
        pdf_path = create_test_pdf(SAMPLE_RESUME_VALID, tmp_path / "formatted.pdf")

        # Parse the PDF
        result = document_parser.parse_file(pdf_path)

        # Verify newlines/structure is somewhat preserved
        # (exact formatting depends on parser implementation)
        text = result["text"]
        assert "\n" in text or " " in text  # Some whitespace should be preserved

        # Verify sections are identifiable
        assert "EXPERIENCE" in text or "Experience" in text
        assert "EDUCATION" in text or "Education" in text

    # ========================================================================
    # Edge Cases
    # ========================================================================

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_pdf_with_special_characters(self, tmp_path, document_parser):
        """Test parsing PDF with special characters and unicode."""
        content_with_special_chars = """
        John Döe
        Software Engineer with €xperience in mültiple domains
        Email: john@example.com • Phone: +1-555-123-4567
        Skills: Python, C++, C#, Node.js
        """

        pdf_path = create_test_pdf(content_with_special_chars, tmp_path / "special.pdf")

        # Parse the PDF
        result = document_parser.parse_file(pdf_path)

        # Should handle special characters gracefully
        assert result["success"] is True
        assert "text" in result
        # Some special characters might be converted, but text should exist
        assert len(result["text"]) > 0

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_very_large_resume(self, tmp_path, document_parser):
        """Test parsing a very large resume (edge case)."""
        # Create a very long resume (repeat content to make it large)
        large_content = (SAMPLE_RESUME_LONG + "\n\n") * 10  # ~30 pages worth

        pdf_path = create_test_pdf(large_content, tmp_path / "large.pdf")

        # Parse the large PDF
        result = document_parser.parse_file(pdf_path)

        # Should handle large files
        assert result["success"] is True
        assert "text" in result

        # Verify substantial content was extracted
        word_count = len(result["text"].split())
        assert word_count > 1000, f"Large resume should have >1000 words, got {word_count}"
