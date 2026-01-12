"""
Mark cover letter as completed
"""
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.enhancement import Enhancement

def mark_complete(enhancement_id: str = None):
    if enhancement_id is None:
        enhancement_id = "56fd018b-cfa5-4568-853a-0f1bb532d942"

    db = SessionLocal()
    try:
        enhancement = db.query(Enhancement).filter(
            Enhancement.id == UUID(enhancement_id)
        ).first()

        if not enhancement:
            print(f"Enhancement {enhancement_id} not found!")
            return

        # Update cover letter status
        enhancement.cover_letter_status = "completed"
        enhancement.cover_letter_path = f"workspace\\resumes\\enhanced\\{enhancement_id}\\cover_letter.md"

        db.commit()
        db.refresh(enhancement)

        print(f"[SUCCESS] Cover letter marked as completed")
        print(f"  Status: {enhancement.cover_letter_status}")
        print(f"  Path: {enhancement.cover_letter_path}")

    finally:
        db.close()

if __name__ == "__main__":
    import sys
    enhancement_id = sys.argv[1] if len(sys.argv) > 1 else None
    mark_complete(enhancement_id)
