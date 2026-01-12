"""Manual style preview generator for Claude Code.

This script is used by Claude Code to manually generate style previews
without requiring an Anthropic API key. Claude Code reads the resume,
generates the previews, and this script saves them to the workspace.
"""

import sys
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.resume import Resume
from uuid import UUID


def save_style_previews(resume_id: str, previews: dict):
    """Save style previews to workspace and update database.

    Args:
        resume_id: Resume UUID as string
        previews: Dictionary of {style_name: preview_text}
    """
    # Validate resume_id
    try:
        resume_uuid = UUID(resume_id)
    except ValueError:
        print(f"Error: Invalid resume ID: {resume_id}")
        sys.exit(1)

    # Get database session
    db: Session = SessionLocal()

    try:
        # Get resume
        resume = db.query(Resume).filter(Resume.id == resume_uuid).first()
        if not resume:
            print(f"Error: Resume not found: {resume_id}")
            sys.exit(1)

        # Create previews directory
        previews_dir = Path("workspace") / "resumes" / "original" / str(resume_id) / "style_previews"
        previews_dir.mkdir(parents=True, exist_ok=True)

        # Save each preview
        for style_name, preview_text in previews.items():
            preview_file = previews_dir / f"{style_name}.txt"
            preview_file.write_text(preview_text, encoding="utf-8")
            print(f"✓ Saved {style_name} preview")

        # Update database
        resume.style_previews_generated = True
        db.commit()

        print(f"\n✅ Successfully generated {len(previews)} style previews for resume {resume_id}")
        print(f"   Previews saved to: {previews_dir}")

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_style_previews.py <resume_id>")
        print("Then paste the previews JSON when prompted")
        sys.exit(1)

    resume_id = sys.argv[1]

    print(f"Generating style previews for resume: {resume_id}")
    print("\nPaste the previews JSON (5 styles):")

    try:
        previews_json = input()
        previews = json.loads(previews_json)

        # Validate we have 5 styles
        expected_styles = ["professional", "executive", "technical", "creative", "concise"]
        if not all(style in previews for style in expected_styles):
            print(f"Error: Missing styles. Expected: {expected_styles}")
            sys.exit(1)

        save_style_previews(resume_id, previews)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
