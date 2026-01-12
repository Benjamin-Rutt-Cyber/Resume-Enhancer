"""
Trigger cover letter generation for completed enhancement
"""
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.enhancement import Enhancement
from app.services.workspace_service import WorkspaceService
from app.services.completion_detector import CompletionDetectorService
from app.api.dependencies import WORKSPACE_ROOT

def trigger_cover_letter():
    enhancement_id = "84a8d470-e59b-4b79-b2d4-0f9d7aa04989"

    db = SessionLocal()
    try:
        enhancement = db.query(Enhancement).filter(
            Enhancement.id == UUID(enhancement_id)
        ).first()

        if not enhancement:
            print(f"Enhancement {enhancement_id} not found!")
            return

        print(f"Current status:")
        print(f"  Resume: {enhancement.status}")
        print(f"  Cover Letter: {enhancement.cover_letter_status}")

        # Create workspace service and completion detector
        workspace_service = WorkspaceService(WORKSPACE_ROOT)
        detector = CompletionDetectorService(workspace_service)

        # Trigger cover letter generation
        print("\nInitiating cover letter generation...")
        detector._initiate_cover_letter_generation(enhancement, db)

        db.refresh(enhancement)

        print(f"\nNew status:")
        print(f"  Resume: {enhancement.status}")
        print(f"  Cover Letter: {enhancement.cover_letter_status}")

        # Check if COVER_LETTER_INSTRUCTIONS.md was created
        instructions_path = WORKSPACE_ROOT / "resumes" / "enhanced" / enhancement_id / "COVER_LETTER_INSTRUCTIONS.md"
        if instructions_path.exists():
            print(f"\n[SUCCESS] Cover letter instructions created at:")
            print(f"  {instructions_path}")
        else:
            print(f"\n[WARNING] Instructions file not found at {instructions_path}")

    finally:
        db.close()

if __name__ == "__main__":
    trigger_cover_letter()
