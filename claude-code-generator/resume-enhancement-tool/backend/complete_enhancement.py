"""
Complete enhancement and trigger cover letter
"""
import sys
from pathlib import Path
from uuid import UUID
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.enhancement import Enhancement
from app.services.workspace_service import WorkspaceService
from app.services.completion_detector import CompletionDetectorService
from app.api.dependencies import WORKSPACE_ROOT

def complete_enhancement(enhancement_id: str):
    db = SessionLocal()
    try:
        enhancement = db.query(Enhancement).filter(
            Enhancement.id == UUID(enhancement_id)
        ).first()

        if not enhancement:
            print(f"Enhancement {enhancement_id} not found!")
            return

        # Mark resume as completed
        enhancement.status = "completed"
        enhancement.completed_at = datetime.now()
        enhancement.output_path = f"workspace\\resumes\\enhanced\\{enhancement_id}\\enhanced.md"
        db.commit()

        print(f"[SUCCESS] Resume completed for {enhancement_id}")

        # Trigger cover letter generation
        workspace_service = WorkspaceService(WORKSPACE_ROOT)
        detector = CompletionDetectorService(workspace_service)

        print("Initiating cover letter generation...")
        detector._initiate_cover_letter_generation(enhancement, db)

        db.refresh(enhancement)

        print(f"Cover letter status: {enhancement.cover_letter_status}")

        # Check if instructions were created
        instructions_path = WORKSPACE_ROOT / "resumes" / "enhanced" / enhancement_id / "COVER_LETTER_INSTRUCTIONS.md"
        if instructions_path.exists():
            print(f"[SUCCESS] Cover letter instructions created")
            return True
        else:
            print(f"[WARNING] Instructions not created")
            return False

    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        enhancement_id = sys.argv[1]
    else:
        enhancement_id = "56fd018b-cfa5-4568-853a-0f1bb532d942"

    complete_enhancement(enhancement_id)
