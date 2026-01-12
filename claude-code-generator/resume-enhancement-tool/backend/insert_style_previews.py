"""
Insert manually generated style previews into the database
"""
import sys
import json
from pathlib import Path
from uuid import UUID

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.resume import Resume

def insert_style_previews():
    # Read the style previews JSON
    previews_file = Path("workspace/resumes/original/cd154f26-7e92-4220-bc52-c93a1c81ce7e/style_previews.json")

    with open(previews_file, 'r') as f:
        data = json.load(f)

    resume_id = UUID(data['resume_id'])  # Convert string to UUID
    previews = data['previews']

    # Create style_previews directory in workspace
    previews_dir = Path("workspace/resumes/original") / str(resume_id) / "style_previews"
    previews_dir.mkdir(parents=True, exist_ok=True)

    # Save each preview as a separate text file
    for preview in previews:
        style_name = preview['style_name']
        preview_text = preview['professional_summary']
        preview_file = previews_dir / f"{style_name}.txt"
        preview_file.write_text(preview_text, encoding='utf-8')
        print(f"  - Saved {style_name}.txt")

    # Update database flag
    db = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            print(f"Resume {resume_id} not found!")
            return

        # Set the flag to True
        resume.style_previews_generated = True
        db.commit()

        print(f"\n[SUCCESS] Generated {len(previews)} style previews for resume {resume_id}")
        print("\nPreviews:")
        for preview in previews:
            print(f"  - {preview['style_name'].upper()}")

    finally:
        db.close()

if __name__ == "__main__":
    insert_style_previews()
