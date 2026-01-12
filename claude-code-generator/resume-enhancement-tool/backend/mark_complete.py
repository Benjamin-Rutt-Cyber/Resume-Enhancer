"""
Manually mark enhancement as completed
"""
import sys
from pathlib import Path
from uuid import UUID
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.enhancement import Enhancement

def mark_complete():
    enhancement_id = "84a8d470-e59b-4b79-b2d4-0f9d7aa04989"

    db = SessionLocal()
    try:
        enhancement = db.query(Enhancement).filter(
            Enhancement.id == UUID(enhancement_id)
        ).first()

        if not enhancement:
            print(f"Enhancement {enhancement_id} not found!")
            return

        # Update status
        enhancement.status = "completed"
        enhancement.completed_at = datetime.utcnow()
        enhancement.output_path = f"workspace\\resumes\\enhanced\\{enhancement_id}\\enhanced.md"

        db.commit()
        db.refresh(enhancement)

        print(f"[SUCCESS] Enhancement {enhancement_id} marked as completed")
        print(f"  Status: {enhancement.status}")
        print(f"  Output Path: {enhancement.output_path}")
        print(f"  Completed At: {enhancement.completed_at}")

    finally:
        db.close()

if __name__ == "__main__":
    mark_complete()
