#!/usr/bin/env python3
"""Update resume to mark style previews as generated."""

import sys
from uuid import UUID
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.resume import Resume

def main():
    db = SessionLocal()
    try:
        resume_id = UUID("9779aa7b-41ed-419a-921d-440c9d2425f6")
        resume = db.query(Resume).filter(Resume.id == resume_id).first()

        if not resume:
            print(f"Resume {resume_id} not found")
            return

        resume.style_previews_generated = True
        db.commit()

        print(f"Updated resume {resume_id} - style_previews_generated = True")

    finally:
        db.close()

if __name__ == "__main__":
    main()
