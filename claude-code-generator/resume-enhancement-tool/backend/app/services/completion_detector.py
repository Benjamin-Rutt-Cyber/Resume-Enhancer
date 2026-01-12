"""Background service to detect enhancement completion and trigger cover letter generation."""

import logging
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from ..models.enhancement import Enhancement
from ..services.workspace_service import WorkspaceService

logger = logging.getLogger(__name__)


class CompletionDetectorService:
    """Detect enhancement completion and trigger cover letter generation."""

    def __init__(self, workspace_service: WorkspaceService):
        self.workspace_service = workspace_service

    def check_and_update_enhancement(self, enhancement: Enhancement, db: Session) -> bool:
        """
        Check if enhancement is complete and trigger cover letter if needed.

        Returns:
            True if any updates were made, False otherwise
        """
        updated = False

        # Step 1: Check if resume is complete
        if enhancement.status == "pending":
            if self._check_resume_complete(enhancement):
                self._mark_resume_complete(enhancement, db)
                updated = True

                # Trigger cover letter generation
                if enhancement.enhancement_type == "job_tailoring" and enhancement.job_id:
                    self._initiate_cover_letter_generation(enhancement, db)
                else:
                    # Skip cover letter for industry revamps
                    enhancement.cover_letter_status = "skipped"
                    db.commit()
                    logger.info(f"Cover letter skipped for enhancement {enhancement.id} (industry revamp)")

        # Step 2: Check if cover letter is complete
        if enhancement.cover_letter_status == "in_progress":
            if self._check_cover_letter_complete(enhancement):
                self._mark_cover_letter_complete(enhancement, db)
                updated = True

        return updated

    def _check_resume_complete(self, enhancement: Enhancement) -> bool:
        """Check if enhanced.md exists."""
        enhanced_md = self.workspace_service.get_enhancement_path(str(enhancement.id)) / "enhanced.md"
        return enhanced_md.exists()

    def _mark_resume_complete(self, enhancement: Enhancement, db: Session):
        """Mark resume as complete."""
        from datetime import datetime
        enhancement.status = "completed"
        enhancement.completed_at = datetime.utcnow()
        enhanced_md = self.workspace_service.get_enhancement_path(str(enhancement.id)) / "enhanced.md"
        enhancement.output_path = str(enhanced_md)
        db.commit()
        logger.info(f"Resume completed for enhancement {enhancement.id}")

    def _initiate_cover_letter_generation(self, enhancement: Enhancement, db: Session):
        """Create COVER_LETTER_INSTRUCTIONS.md to trigger generation."""
        try:
            # Get resume to fetch style
            from ..models.resume import Resume
            resume = db.query(Resume).filter(Resume.id == enhancement.resume_id).first()
            style = resume.selected_style if resume else None

            # Create cover letter instructions
            instructions_path = self.workspace_service.create_cover_letter_instructions(
                enhancement_id=str(enhancement.id),
                resume_id=str(enhancement.resume_id),
                job_id=str(enhancement.job_id),
                enhancement_type=enhancement.enhancement_type,
                style=style,
            )

            if instructions_path:
                enhancement.cover_letter_status = "in_progress"
                db.commit()
                logger.info(f"Cover letter generation initiated for enhancement {enhancement.id}")
            else:
                enhancement.cover_letter_status = "skipped"
                db.commit()

        except Exception as e:
            logger.error(f"Failed to initiate cover letter generation for {enhancement.id}: {e}")
            enhancement.cover_letter_status = "failed"
            enhancement.cover_letter_error = str(e)
            db.commit()

    def _check_cover_letter_complete(self, enhancement: Enhancement) -> bool:
        """Check if cover_letter.md exists."""
        cover_letter_md = self.workspace_service.get_enhancement_path(str(enhancement.id)) / "cover_letter.md"
        return cover_letter_md.exists()

    def _mark_cover_letter_complete(self, enhancement: Enhancement, db: Session):
        """Mark cover letter as complete."""
        cover_letter_md = self.workspace_service.get_enhancement_path(str(enhancement.id)) / "cover_letter.md"
        enhancement.cover_letter_path = str(cover_letter_md)
        enhancement.cover_letter_status = "completed"
        db.commit()
        logger.info(f"Cover letter completed for enhancement {enhancement.id}")
