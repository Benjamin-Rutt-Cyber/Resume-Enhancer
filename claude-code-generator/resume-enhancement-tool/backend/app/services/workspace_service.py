"""Workspace service for managing resume files and enhancement requests."""

from pathlib import Path
from uuid import uuid4
from typing import Dict, Optional, Tuple
import shutil
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkspaceService:
    """
    Manage workspace files for resumes, jobs, and enhancements.

    This service creates and manages the file structure that Claude Code
    will read from and write to.
    """

    def __init__(self, workspace_root: Path):
        """
        Initialize workspace service.

        Args:
            workspace_root: Root directory for workspace files
        """
        self.workspace_root = workspace_root
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure all required workspace directories exist."""
        directories = [
            "resumes/original",
            "resumes/enhanced",
            "jobs",
            "templates/resume_formats",
            "templates/styles",
            "_instructions/industries",
        ]

        for dir_path in directories:
            full_path = self.workspace_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Workspace directories ensured at {self.workspace_root}")

    def store_resume(
        self,
        file_path: Path,
        extracted_text: str,
        metadata: Dict,
    ) -> Tuple[str, Path]:
        """
        Store an uploaded resume in the workspace.

        Args:
            file_path: Path to the uploaded resume file
            extracted_text: Text extracted from the resume
            metadata: Metadata about the resume (filename, format, etc.)

        Returns:
            Tuple of (resume_id, resume_directory_path)
        """
        resume_id = str(uuid4())
        resume_dir = self.workspace_root / "resumes" / "original" / resume_id
        resume_dir.mkdir(parents=True, exist_ok=True)

        # Copy original file
        source_extension = file_path.suffix
        dest_file = resume_dir / f"source{source_extension}"
        shutil.copy(file_path, dest_file)

        # Save extracted text (for Claude Code to read)
        with open(resume_dir / "extracted.txt", "w", encoding="utf-8") as f:
            f.write(extracted_text)

        # Save metadata
        metadata_with_timestamp = {
            **metadata,
            "resume_id": resume_id,
            "stored_at": datetime.utcnow().isoformat(),
            "source_file": f"source{source_extension}",
        }

        with open(resume_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata_with_timestamp, f, indent=2)

        logger.info(f"Resume stored: {resume_id}")

        return resume_id, resume_dir

    def store_job(
        self,
        description: str,
        metadata: Dict,
    ) -> Tuple[str, Path]:
        """
        Store a job description in the workspace.

        Args:
            description: Job description text
            metadata: Metadata about the job (title, company, etc.)

        Returns:
            Tuple of (job_id, job_directory_path)
        """
        job_id = str(uuid4())
        job_dir = self.workspace_root / "jobs" / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # Save job description
        with open(job_dir / "description.txt", "w", encoding="utf-8") as f:
            f.write(description)

        # Save metadata
        metadata_with_timestamp = {
            **metadata,
            "job_id": job_id,
            "stored_at": datetime.utcnow().isoformat(),
        }

        with open(job_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata_with_timestamp, f, indent=2)

        logger.info(f"Job description stored: {job_id}")

        return job_id, job_dir

    def create_enhancement_workspace(
        self,
        resume_id: str,
        job_id: Optional[str],
        enhancement_type: str,
        industry: Optional[str] = None,
    ) -> Tuple[str, Path]:
        """
        Create a workspace for a resume enhancement request.

        This creates an INSTRUCTIONS.md file that tells Claude Code what to do.

        Args:
            resume_id: ID of the resume to enhance
            job_id: ID of the job description (for job_tailoring type)
            enhancement_type: Type of enhancement ('job_tailoring' or 'industry_revamp')
            industry: Industry for revamp (required for industry_revamp type)

        Returns:
            Tuple of (enhancement_id, enhancement_directory_path)
        """
        enhancement_id = str(uuid4())
        enhancement_dir = self.workspace_root / "resumes" / "enhanced" / enhancement_id
        enhancement_dir.mkdir(parents=True, exist_ok=True)

        # Create INSTRUCTIONS.md for Claude Code
        instructions = self._create_instructions(
            enhancement_id,
            resume_id,
            job_id,
            enhancement_type,
            industry,
        )

        with open(enhancement_dir / "INSTRUCTIONS.md", "w", encoding="utf-8") as f:
            f.write(instructions)

        # Create metadata file
        metadata = {
            "enhancement_id": enhancement_id,
            "resume_id": resume_id,
            "job_id": job_id,
            "enhancement_type": enhancement_type,
            "industry": industry,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
        }

        with open(enhancement_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Enhancement workspace created: {enhancement_id}")

        return enhancement_id, enhancement_dir

    def _create_instructions(
        self,
        enhancement_id: str,
        resume_id: str,
        job_id: Optional[str],
        enhancement_type: str,
        industry: Optional[str],
    ) -> str:
        """
        Create INSTRUCTIONS.md content for Claude Code.

        Args:
            enhancement_id: Enhancement ID
            resume_id: Resume ID
            job_id: Job ID (optional)
            enhancement_type: Type of enhancement
            industry: Industry (optional)

        Returns:
            Markdown formatted instructions
        """
        if enhancement_type == "job_tailoring":
            return self._create_job_tailoring_instructions(
                enhancement_id, resume_id, job_id
            )
        elif enhancement_type == "industry_revamp":
            return self._create_industry_revamp_instructions(
                enhancement_id, resume_id, industry
            )
        else:
            raise ValueError(f"Unknown enhancement type: {enhancement_type}")

    def _create_job_tailoring_instructions(
        self,
        enhancement_id: str,
        resume_id: str,
        job_id: str,
    ) -> str:
        """Create instructions for job-specific tailoring."""
        return f"""# Resume Enhancement Request - Job Tailoring

**Enhancement ID:** `{enhancement_id}`
**Type:** Job-Specific Tailoring
**Status:** Pending

## Task

Tailor the provided resume to match the specific job description. Focus on:
- Matching keywords from the job description
- Highlighting relevant experience and skills
- Quantifying achievements where possible
- Keeping the resume ATS-friendly

## Input Files

- **Resume:** `workspace/resumes/original/{resume_id}/extracted.txt`
- **Job Description:** `workspace/jobs/{job_id}/description.txt`

## Output File

Write the enhanced resume to:
**`workspace/resumes/enhanced/{enhancement_id}/enhanced.md`**

## Requirements

1. **Keyword Matching:** Incorporate relevant keywords from the job description
2. **Highlight Relevance:** Emphasize experiences and skills that match the job
3. **Quantify:** Use metrics and numbers where possible (e.g., "increased by 35%")
4. **Action Verbs:** Use strong action verbs (Led, Developed, Implemented, Designed)
5. **ATS-Friendly:** Use standard markdown formatting (no tables, no images)
6. **Truthful:** Never fabricate information - only enhance and reorganize existing content

## Output Format

Use markdown with clear sections:

```markdown
# [Name]
[Contact Information]

## Professional Summary
[2-3 sentences tailored to the job]

## Skills
- [Relevant skill 1]
- [Relevant skill 2]
...

## Professional Experience

### [Job Title] - [Company]
*[Start Date] - [End Date]*

- [Achievement with metrics]
- [Another achievement]
...

## Education
[Degrees and certifications]

## Additional Sections (if applicable)
[Projects, Publications, etc.]
```

## When Complete

After writing `enhanced.md`, the backend will:
1. Convert markdown to PDF
2. Notify the user
3. Make it available for download

---

**Created:** {datetime.utcnow().isoformat()}
"""

    def _create_industry_revamp_instructions(
        self,
        enhancement_id: str,
        resume_id: str,
        industry: str,
    ) -> str:
        """Create instructions for industry-focused revamp."""
        return f"""# Resume Enhancement Request - Industry Revamp

**Enhancement ID:** `{enhancement_id}`
**Type:** Industry-Focused Revamp
**Industry:** {industry}
**Status:** Pending

## Task

Perform a comprehensive revamp of the resume for the **{industry}** industry.
This is more extensive than job tailoring - completely restructure and optimize
the resume for the target industry.

## Input Files

- **Resume:** `workspace/resumes/original/{resume_id}/extracted.txt`
- **Industry Guide:** `workspace/_instructions/industries/{industry.lower().replace(' ', '_')}.md`

## Output File

Write the revamped resume to:
**`workspace/resumes/enhanced/{enhancement_id}/enhanced.md`**

## Requirements

1. **Industry Standards:** Follow best practices for {industry} resumes (see industry guide)
2. **Comprehensive Restructure:** Reorganize sections to match industry expectations
3. **Terminology:** Use industry-specific terminology and keywords
4. **Emphasis:** Highlight most relevant experiences for {industry}
5. **Certifications:** Emphasize relevant certifications and training
6. **Format:** Use modern, professional formatting appropriate for {industry}
7. **Truthful:** Never fabricate - only enhance and reorganize existing content

## Process

1. Read the resume: `workspace/resumes/original/{resume_id}/extracted.txt`
2. Read the industry guide: `workspace/_instructions/industries/{industry.lower().replace(' ', '_')}.md`
3. Analyze what changes are needed for {industry}
4. Comprehensively rewrite the resume following industry best practices
5. Write enhanced resume to: `workspace/resumes/enhanced/{enhancement_id}/enhanced.md`

## Output Format

Follow the format recommendations in the industry guide. Generally:

```markdown
# [Name]
[Contact Information]

## Professional Summary
[3-4 sentences tailored to {industry}]

## [Industry-Specific Sections]
[Follow industry guide structure]

## Professional Experience
[Restructured for {industry} focus]

## Education & Certifications
[Emphasize relevant credentials]

## [Additional Sections]
[As recommended in industry guide]
```

## When Complete

After writing `enhanced.md`, the backend will:
1. Convert markdown to PDF
2. Notify the user
3. Make it available for download

---

**Created:** {datetime.utcnow().isoformat()}
"""

    def get_resume_path(self, resume_id: str) -> Path:
        """Get path to a resume directory."""
        return self.workspace_root / "resumes" / "original" / resume_id

    def get_job_path(self, job_id: str) -> Path:
        """Get path to a job directory."""
        return self.workspace_root / "jobs" / job_id

    def get_enhancement_path(self, enhancement_id: str) -> Path:
        """Get path to an enhancement directory."""
        return self.workspace_root / "resumes" / "enhanced" / enhancement_id

    def check_enhancement_complete(self, enhancement_id: str) -> bool:
        """
        Check if Claude Code has completed the enhancement.

        Args:
            enhancement_id: Enhancement ID

        Returns:
            True if enhanced.md exists
        """
        enhancement_dir = self.get_enhancement_path(enhancement_id)
        enhanced_file = enhancement_dir / "enhanced.md"
        return enhanced_file.exists()

    def list_pending_enhancements(self) -> list[Dict]:
        """
        List all pending enhancements (INSTRUCTIONS.md exists, enhanced.md doesn't).

        Returns:
            List of pending enhancement metadata
        """
        enhanced_dir = self.workspace_root / "resumes" / "enhanced"
        pending = []

        if not enhanced_dir.exists():
            return pending

        for enhancement_dir in enhanced_dir.iterdir():
            if not enhancement_dir.is_dir():
                continue

            instructions_file = enhancement_dir / "INSTRUCTIONS.md"
            enhanced_file = enhancement_dir / "enhanced.md"
            metadata_file = enhancement_dir / "metadata.json"

            if instructions_file.exists() and not enhanced_file.exists():
                if metadata_file.exists():
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    pending.append(metadata)

        return pending
