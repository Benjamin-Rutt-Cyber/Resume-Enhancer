"""
Background worker for processing resume enhancements using Claude API.

This worker polls the database for pending enhancements and processes them
automatically using the Anthropic Claude API.
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from anthropic import Anthropic

from app.core.database import SessionLocal, engine
from app.models.enhancement import Enhancement
from app.core.config import settings
from app.utils.pdf_generator import PDFGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancementWorker:
    """Background worker for processing resume enhancements."""

    def __init__(self):
        """Initialize the worker."""
        self.workspace_root = Path(settings.WORKSPACE_ROOT)

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        # Remove proxy settings that cause issues in Docker
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)

        self.client = Anthropic(api_key=api_key)

        # Initialize PDF generator
        templates_dir = self.workspace_root / "templates"
        self.pdf_generator = PDFGenerator(templates_dir)

        logger.info("EnhancementWorker initialized successfully")
        logger.info(f"Workspace root: {self.workspace_root}")
        logger.info(f"API key configured: {api_key[:20]}...")

    def get_pending_enhancements(self, db: Session) -> list[Enhancement]:
        """Get all pending enhancements from database."""
        return db.query(Enhancement).filter(
            Enhancement.status == "pending"
        ).order_by(Enhancement.created_at).all()

    def get_pending_cover_letters(self, db: Session) -> list[Enhancement]:
        """Get all enhancements with pending cover letters."""
        return db.query(Enhancement).filter(
            Enhancement.status == "completed",
            Enhancement.job_id.isnot(None),
            Enhancement.cover_letter_status == "pending"
        ).order_by(Enhancement.created_at).all()

    def read_file(self, file_path: Path) -> str:
        """Read file contents safely."""
        try:
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return ""
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""

    def process_enhancement(self, enhancement: Enhancement, db: Session) -> bool:
        """
        Process a single enhancement using Claude API.

        Args:
            enhancement: Enhancement object to process
            db: Database session

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Processing enhancement {enhancement.id}")

        try:
            # Build paths
            enhancement_dir = self.workspace_root / "resumes" / "enhanced" / str(enhancement.id)
            resume_dir = self.workspace_root / "resumes" / "original" / str(enhancement.resume_id)

            # Read required files
            instructions_path = enhancement_dir / "INSTRUCTIONS.md"
            resume_path = resume_dir / "extracted.txt"

            instructions = self.read_file(instructions_path)
            resume_text = self.read_file(resume_path)

            if not instructions or not resume_text:
                raise ValueError("Missing required files (INSTRUCTIONS.md or resume)")

            # Read job description if this is job tailoring
            job_description = ""
            if enhancement.job_id:
                job_dir = self.workspace_root / "jobs" / str(enhancement.job_id)
                job_path = job_dir / "description.txt"
                job_description = self.read_file(job_path)

            # Build prompt for Claude
            prompt = self._build_prompt(instructions, resume_text, job_description, enhancement)

            logger.info(f"Calling Claude API for enhancement {enhancement.id}")
            logger.info(f"Prompt length: {len(prompt)} characters")

            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract the enhanced resume from response
            enhanced_resume = response.content[0].text

            logger.info(f"Claude API response received ({len(enhanced_resume)} characters)")

            # Save enhanced resume
            output_path = enhancement_dir / "enhanced.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_resume)

            logger.info(f"Saved enhanced resume to {output_path}")

            # Generate PDF from markdown
            pdf_path = enhancement_dir / "enhanced.pdf"
            logger.info(f"Generating PDF for enhancement {enhancement.id}")

            pdf_result = self.pdf_generator.markdown_to_pdf(
                markdown_path=output_path,
                output_path=pdf_path,
                template="modern"
            )

            if pdf_result.get("success"):
                logger.info(f"PDF generated successfully: {pdf_path}")
            else:
                logger.error(f"PDF generation failed: {pdf_result.get('error')}")

            # Update enhancement in database
            enhancement.output_path = f"workspace/resumes/enhanced/{enhancement.id}/enhanced.md"
            enhancement.pdf_path = f"workspace/resumes/enhanced/{enhancement.id}/enhanced.pdf" if pdf_result.get("success") else None
            enhancement.status = "completed"
            enhancement.completed_at = datetime.utcnow()
            db.commit()

            logger.info(f"Enhancement {enhancement.id} completed successfully")

            # Generate cover letter if this is a job tailoring enhancement
            if enhancement.job_id:
                logger.info(f"Generating cover letter for enhancement {enhancement.id}")
                self.process_cover_letter(enhancement, db)

            return True

        except Exception as e:
            logger.error(f"Error processing enhancement {enhancement.id}: {e}", exc_info=True)

            # Update enhancement with error
            enhancement.status = "failed"
            enhancement.error_message = str(e)
            db.commit()

            return False

    def process_cover_letter(self, enhancement: Enhancement, db: Session) -> bool:
        """
        Generate a cover letter for the enhancement.

        Args:
            enhancement: Enhancement object
            db: Database session

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing cover letter for enhancement {enhancement.id}")

            # Build paths
            enhancement_dir = self.workspace_root / "resumes" / "enhanced" / str(enhancement.id)
            resume_path = enhancement_dir / "enhanced.md"
            job_dir = self.workspace_root / "jobs" / str(enhancement.job_id)
            job_path = job_dir / "description.txt"

            # Read files
            enhanced_resume = self.read_file(resume_path)
            job_description = self.read_file(job_path)

            if not enhanced_resume or not job_description:
                raise ValueError("Missing enhanced resume or job description")

            # Build cover letter prompt
            prompt = self._build_cover_letter_prompt(enhanced_resume, job_description, enhancement)

            logger.info(f"Calling Claude API for cover letter {enhancement.id}")

            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract cover letter
            cover_letter = response.content[0].text

            logger.info(f"Cover letter generated ({len(cover_letter)} characters)")

            # Save cover letter
            cover_letter_path = enhancement_dir / "cover_letter.md"
            with open(cover_letter_path, 'w', encoding='utf-8') as f:
                f.write(cover_letter)

            logger.info(f"Saved cover letter to {cover_letter_path}")

            # Generate PDF from cover letter markdown
            cover_letter_pdf_path = enhancement_dir / "cover_letter.pdf"
            logger.info(f"Generating cover letter PDF for enhancement {enhancement.id}")

            cover_pdf_result = self.pdf_generator.markdown_to_pdf(
                markdown_path=cover_letter_path,
                output_path=cover_letter_pdf_path,
                template="modern"
            )

            if cover_pdf_result.get("success"):
                logger.info(f"Cover letter PDF generated successfully: {cover_letter_pdf_path}")
            else:
                logger.error(f"Cover letter PDF generation failed: {cover_pdf_result.get('error')}")

            # Update enhancement in database
            enhancement.cover_letter_path = f"workspace/resumes/enhanced/{enhancement.id}/cover_letter.md"
            enhancement.cover_letter_pdf_path = f"workspace/resumes/enhanced/{enhancement.id}/cover_letter.pdf" if cover_pdf_result.get("success") else None
            enhancement.cover_letter_status = "completed"
            db.commit()

            logger.info(f"Cover letter for enhancement {enhancement.id} completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error processing cover letter for {enhancement.id}: {e}", exc_info=True)

            # Update enhancement with error
            enhancement.cover_letter_status = "failed"
            enhancement.cover_letter_error = str(e)
            db.commit()

            return False

    def _build_cover_letter_prompt(
        self,
        enhanced_resume: str,
        job_description: str,
        enhancement: Enhancement
    ) -> str:
        """Build the prompt for cover letter generation."""

        prompt = f"""You are a professional cover letter writer. Your task is to create a compelling cover letter that complements the provided resume and is tailored to the specific job description.

# ENHANCED RESUME

{enhanced_resume}

# JOB DESCRIPTION

{job_description}

# COVER LETTER REQUIREMENTS

**Length:** 175-200 words maximum (STRICT LIMIT - single page only)
**Style:** Professional, formal tone matching the resume
**Format:** Standard business letter format in markdown

**Structure:**
1. **Opening paragraph (40-50 words):** Express interest in the specific role and company
2. **Body paragraph (80-100 words):** Highlight 2-3 most relevant qualifications from resume that match job requirements
3. **Closing paragraph (40-50 words):** Express enthusiasm and call to action

**Guidelines:**
- Use CONCISE, direct language (no verbose explanations)
- Match keywords from the job description
- Reference specific achievements from the resume
- Demonstrate understanding of the role requirements
- Show genuine interest in the company/position
- NO generic phrases like "I am writing to apply"
- NO restating entire resume
- Focus on value proposition and fit

**Word Count Validation:**
Before submitting, count words. Must be 175-200 words total (NOT 262 words).
If over 200 words, cut content aggressively.

# YOUR TASK

Generate a professional cover letter following ALL requirements above. Output ONLY the cover letter in markdown format - do not include any explanations or commentary.

Output the cover letter now:
"""

        return prompt

    def _build_prompt(
        self,
        instructions: str,
        resume_text: str,
        job_description: str,
        enhancement: Enhancement
    ) -> str:
        """Build the prompt for Claude API."""

        prompt = f"""You are a professional resume writer. Your task is to enhance a resume according to the specific instructions provided.

# INSTRUCTIONS

{instructions}

# ORIGINAL RESUME

{resume_text}
"""

        if job_description:
            prompt += f"""
# JOB DESCRIPTION

{job_description}

Please tailor the resume specifically for this job posting. Match keywords, highlight relevant experience, and align the resume with the job requirements.
"""

        prompt += """
# YOUR TASK

Generate an enhanced resume following ALL the instructions above. Output ONLY the enhanced resume in markdown format - do not include any explanations, notes, or commentary.

The enhanced resume should:
1. Follow the exact formatting rules specified in the instructions
2. Match the selected writing style
3. Stay within the word count limits
4. Be tailored to the job description (if provided)
5. Include quantifiable achievements and metrics where possible
6. Be ATS-optimized with proper keyword usage

Output the enhanced resume now:
"""

        return prompt

    def run(self, poll_interval: int = 10):
        """
        Run the worker in a continuous loop.

        Args:
            poll_interval: Seconds to wait between polling cycles
        """
        logger.info(f"Worker started. Polling every {poll_interval} seconds...")

        while True:
            try:
                # Create database session
                db = SessionLocal()

                try:
                    # Get pending enhancements
                    pending = self.get_pending_enhancements(db)

                    if pending:
                        logger.info(f"Found {len(pending)} pending enhancement(s)")

                        for enhancement in pending:
                            logger.info(f"Processing enhancement {enhancement.id}")
                            self.process_enhancement(enhancement, db)
                    else:
                        logger.debug("No pending enhancements")

                    # Get pending cover letters
                    pending_cover_letters = self.get_pending_cover_letters(db)

                    if pending_cover_letters:
                        logger.info(f"Found {len(pending_cover_letters)} pending cover letter(s)")

                        for enhancement in pending_cover_letters:
                            logger.info(f"Processing cover letter for {enhancement.id}")
                            self.process_cover_letter(enhancement, db)
                    else:
                        logger.debug("No pending cover letters")

                finally:
                    db.close()

            except Exception as e:
                logger.error(f"Error in worker loop: {e}", exc_info=True)

            # Write heartbeat
            try:
                # Count total enhancements to verify DB integrity
                total_enhancements = db.query(Enhancement).count()
                pending_count = len(pending) if 'pending' in locals() else 0
                
                with open(self.workspace_root / "worker_heartbeat.json", "w") as f:
                    import json
                    status = {
                        "last_beat": datetime.now().isoformat(),
                        "status": "running",
                        "api_key_configured": bool(self.client.api_key),
                        "pending_enhancements": pending_count,
                        "total_db_records": total_enhancements,
                        "db_url_masked": str(settings.DATABASE_URL).split("@")[-1] if "@" in str(settings.DATABASE_URL) else "sqlite"
                    }
                    json.dump(status, f)
            except Exception as hb_err:
                logger.error(f"Failed to write heartbeat: {hb_err}")

            # Wait before next poll
            time.sleep(poll_interval)


def main():
    """Main entry point for the worker."""
    logger.info("Starting Enhancement Worker...")

    # Verify database connection
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        sys.exit(1)


    # Create and run worker
    try:
        worker = EnhancementWorker()
        worker.run(poll_interval=10)
    except Exception as e:
        logger.critical(f"Worker failed to start: {e}", exc_info=True)
        # Write error to workspace for debugging
        try:
            os.makedirs("workspace", exist_ok=True)
            with open("workspace/worker_crash.log", "w") as f:
                f.write(f"Worker crashed at {datetime.now()}:\n{str(e)}")
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
