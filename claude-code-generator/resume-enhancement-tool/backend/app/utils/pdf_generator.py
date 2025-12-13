"""PDF generator for converting markdown resumes to PDF."""

from pathlib import Path
from typing import Optional, Dict
import markdown
from weasyprint import HTML, CSS
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Convert markdown resumes to professionally formatted PDFs."""

    def __init__(self, templates_dir: Path):
        """
        Initialize PDF generator.

        Args:
            templates_dir: Directory containing HTML templates
        """
        self.templates_dir = templates_dir
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def markdown_to_pdf(
        self,
        markdown_path: Path,
        output_path: Path,
        template: str = "modern",
        custom_css: Optional[str] = None,
    ) -> Dict[str, any]:
        """
        Convert markdown file to PDF using HTML template.

        Args:
            markdown_path: Path to markdown file
            output_path: Path for output PDF file
            template: Template name (modern, professional, ats_friendly)
            custom_css: Optional custom CSS string

        Returns:
            Dictionary with generation results

        Raises:
            FileNotFoundError: If markdown file or template doesn't exist
        """
        try:
            # Read markdown content
            with open(markdown_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # Convert markdown to HTML
            html_content = markdown.markdown(
                md_content,
                extensions=[
                    "tables",  # Support tables
                    "nl2br",  # New line to <br>
                    "fenced_code",  # Code blocks
                    "sane_lists",  # Better list handling
                ],
            )

            # Load HTML template
            template_path = self.templates_dir / "resume_formats" / f"{template}.html"

            if not template_path.exists():
                logger.warning(
                    f"Template {template} not found, using default inline template"
                )
                template_html = self._get_default_template()
            else:
                with open(template_path, "r", encoding="utf-8") as f:
                    template_html = f.read()

            # Insert content into template
            full_html = template_html.replace("{{content}}", html_content)

            # Load CSS if provided
            css_objects = []
            if custom_css:
                css_objects.append(CSS(string=custom_css))

            # Convert HTML to PDF using WeasyPrint
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if css_objects:
                HTML(string=full_html).write_pdf(output_path, stylesheets=css_objects)
            else:
                HTML(string=full_html).write_pdf(output_path)

            logger.info(f"Successfully generated PDF: {output_path}")

            return {
                "success": True,
                "output_path": str(output_path),
                "size_bytes": output_path.stat().st_size,
                "template": template,
            }

        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return {
                "success": False,
                "error": f"File not found: {e}",
            }
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def _get_default_template(self) -> str:
        """
        Get default HTML template if custom template not found.

        Returns:
            HTML template string
        """
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: letter;
            margin: 0.75in;
        }

        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
            margin: 0;
            padding: 0;
        }

        h1 {
            color: #2c3e50;
            font-size: 28px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
            margin-top: 0;
        }

        h2 {
            color: #34495e;
            font-size: 20px;
            margin-top: 25px;
            margin-bottom: 10px;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }

        h3 {
            color: #555;
            font-size: 16px;
            margin-top: 15px;
            margin-bottom: 5px;
        }

        p {
            margin: 8px 0;
        }

        ul, ol {
            margin: 10px 0;
            padding-left: 25px;
        }

        li {
            margin: 5px 0;
        }

        strong {
            color: #2c3e50;
        }

        em {
            font-style: italic;
            color: #7f8c8d;
        }

        a {
            color: #3498db;
            text-decoration: none;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }

        th, td {
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }

        code {
            background-color: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 90%;
        }

        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-left: 0;
            color: #555;
            font-style: italic;
        }

        /* Print-specific styles */
        @media print {
            body {
                font-size: 11pt;
            }

            h1 {
                page-break-after: avoid;
            }

            h2, h3 {
                page-break-after: avoid;
            }

            ul, ol {
                page-break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    {{content}}
</body>
</html>"""

    def validate_markdown(self, markdown_path: Path) -> Dict[str, any]:
        """
        Validate markdown file before conversion.

        Args:
            markdown_path: Path to markdown file

        Returns:
            Dictionary with validation results
        """
        if not markdown_path.exists():
            return {
                "valid": False,
                "error": "Markdown file does not exist",
            }

        try:
            with open(markdown_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                return {
                    "valid": False,
                    "error": "Markdown file is empty",
                }

            # Check for common resume sections
            required_sections = ["#"]  # At least one heading
            has_sections = any(section in content for section in required_sections)

            if not has_sections:
                return {
                    "valid": False,
                    "error": "No markdown headings found",
                    "warning": "File may not be properly formatted",
                }

            return {
                "valid": True,
                "size_bytes": len(content.encode("utf-8")),
                "lines": len(content.split("\n")),
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Error reading markdown: {str(e)}",
            }
