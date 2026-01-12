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
        style: Optional[str] = None,
    ) -> Tuple[str, Path]:
        """
        Create a workspace for a resume enhancement request.

        This creates an INSTRUCTIONS.md file that tells Claude Code what to do.

        Args:
            resume_id: ID of the resume to enhance
            job_id: ID of the job description (for job_tailoring type)
            enhancement_type: Type of enhancement ('job_tailoring' or 'industry_revamp')
            industry: Industry for revamp (required for industry_revamp type)
            style: Writing style preference (optional)

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
            style,
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

        # Create validation hint for style validation (only for job_tailoring)
        if enhancement_type == "job_tailoring" and job_id and style:
            validation_hint = {
                "resume_id": resume_id,
                "job_id": job_id,
                "selected_style": style,
                "requires_validation": True,
            }
            hint_file = enhancement_dir / "STYLE_VALIDATION_HINT.json"
            with open(hint_file, "w", encoding="utf-8") as f:
                json.dump(validation_hint, f, indent=2)
            logger.info(f"Style validation hint created for enhancement {enhancement_id}")

        logger.info(f"Enhancement workspace created: {enhancement_id}")

        return enhancement_id, enhancement_dir

    def _create_instructions(
        self,
        enhancement_id: str,
        resume_id: str,
        job_id: Optional[str],
        enhancement_type: str,
        industry: Optional[str],
        style: Optional[str] = None,
    ) -> str:
        """
        Create INSTRUCTIONS.md content for Claude Code.

        Args:
            enhancement_id: Enhancement ID
            resume_id: Resume ID
            job_id: Job ID (optional)
            enhancement_type: Type of enhancement
            industry: Industry (optional)
            style: Writing style (optional)

        Returns:
            Markdown formatted instructions
        """
        if enhancement_type == "job_tailoring":
            return self._create_job_tailoring_instructions(
                enhancement_id, resume_id, job_id, style
            )
        elif enhancement_type == "industry_revamp":
            return self._create_industry_revamp_instructions(
                enhancement_id, resume_id, industry, style
            )
        else:
            raise ValueError(f"Unknown enhancement type: {enhancement_type}")

    def _create_job_tailoring_instructions(
        self,
        enhancement_id: str,
        resume_id: str,
        job_id: str,
        style: Optional[str] = None,
    ) -> str:
        """Create instructions for job-specific tailoring."""
        # Import here to avoid circular dependency
        from ..config.styles import STYLES

        style_guidance = ""
        if style and style in STYLES:
            style_config = STYLES[style]
            style_guidance = f"""
## Style Guidelines

The user has selected the **{style_config['name']}** writing style for their resume.

**Style Characteristics:**
- Tone: {style_config['tone']}
- Approach: {style_config['prompt_guidance']}

**IMPORTANT:** Apply this style consistently throughout the entire enhanced resume. The user has already seen a professional summary preview in this style, so maintain that tone and approach across all sections.

"""

        return f"""# Resume Enhancement Request - Job Tailoring

**Enhancement ID:** `{enhancement_id}`
**Type:** Job-Specific Tailoring
**Status:** Pending

{style_guidance}
## Length Requirements (CRITICAL - MUST FOLLOW - 2026 BEST PRACTICES)

**Target Page Length:** Based on 2026 industry research
- Entry-level (0-5 years): **1 PAGE ONLY** (not 2 pages)
- Mid-level (5-10 years): 1-2 pages
- Senior (10+ years): 2 pages MAX

**ABSOLUTE MAXIMUM WORD COUNTS:**
- Entry-level (0-5 years): **400 WORDS MAX** = 1 PAGE ONLY
- Mid-level (5-10 years): **600 WORDS MAX** = 1-2 PAGES
- Senior (10+ years): **800 WORDS MAX** = 2 PAGES (fill both pages)

**CRITICAL:** Count words BEFORE adding markdown syntax. If over limit, CUT content aggressively.

**STRICT LIMITS:**
- NEVER exceed 2 pages regardless of experience
- NEVER exceed word count maximums (400/600/800)
- Entry-level MUST be 1 page (66% of employers require this)
- Minimize white space - use 0.5-0.75" margins if needed
- Line spacing: 1.0-1.15 (single-spaced)

## Formatting Rules (ULTRA-STRICT - ZERO WHITE SPACE TOLERANCE)

❌ **ABSOLUTELY FORBIDDEN:**
- NO decorative dividers (`---` or `===`)
- NO emojis or special characters
- NO blank lines between bullets
- NO blank lines between skill categories
- NO blank lines in Education section
- NO blank lines in Certifications section
- NO custom creative headers
- NO more than 3-4 jobs listed
- NO tables, text boxes, or graphics
- NO "Professional Development" or "Hobbies" sections for entry-level
- NO "Relevant Coursework" expansions in Education
- NO certification descriptions (title and date ONLY)

✅ **STRICT REQUIREMENTS:**
- ONLY 4-5 blank lines in ENTIRE document (one between each major section)
- Contact info: ONE line with pipes (|) separating elements
- Professional Summary: 2-3 sentences (40-60 words MAX), NO blank lines before/after
- Skills: Single-line categories with pipes (see format below), NO multi-line categories
- Each job: Title/Company/Dates, then bullets immediately following
- Education: Degree, University, Location, Dates - ONE line per degree, NO coursework
- Certifications: Name - Issuer | Date - ONE line per cert, NO descriptions
- Lead every bullet with action verb + quantified result

## Skills Section Format (REQUIRED - SINGLE-LINE CATEGORIES)

**WRONG (wastes 8+ lines):**
```
## Skills
**System Administration:** Windows Server, Active Directory...

**Infrastructure & Tools:** Azure, ServiceNow...

**Networking & Security:** TCP/IP, DNS/DHCP...
```

**CORRECT (3-4 lines total with pipe-separated categories):**
```
## Skills
**System Administration:** Windows Server, Active Directory, Microsoft 365, DNS/DHCP, Group Policy | **Infrastructure:** Azure, ServiceNow, Cherwell ITSM, TeamViewer, PowerShell, Virtual Machines | **Networking:** TCP/IP, Network Troubleshooting, Security Compliance | **Technical:** Windows 10/11, Linux, Documentation
```

**Format rules:**
- Maximum 3-4 category groups
- Each category on SAME line, separated by ` | `
- NO blank lines between categories
- Total Skills section: 2-4 lines maximum

## Education & Certifications Format (ULTRA-CONDENSED)

**Education - WRONG:**
```
**Bachelor of Cybersecurity** - Griffith University, Brisbane, QLD | March 2024 - 2026

Relevant Coursework: Applied Network Security, Database Design...
```

**Education - CORRECT:**
```
## Education
**Bachelor of Cybersecurity** - Griffith University, Brisbane, QLD | 2024-2026
**Diploma of Information Technology** - Griffith College, Brisbane, QLD | 2022-2023
```

**Certifications - WRONG:**
```
**IT Support Technical Skills** - Udemy | June 2025

Gained hands-on experience with Active Directory...
```

**Certifications - CORRECT (Name and date ONLY):**
```
## Certifications
IT Support Technical Skills Helpdesk - Udemy | 2025
Computer Systems and Networks - Griffith College | 2023
Advent of Cyber - TryHackMe | 2024
```

**Format rules:**
- ONE line per certification
- NO descriptions or details whatsoever
- NO blank lines between certifications
- Format: `[Certification Name] - [Issuer] | [Year]`

## Bullet Point Guidelines (CRITICAL - VARIES BY JOB)

**Most Recent/Relevant Job:** 4-5 bullets
**Second Most Recent Job:** 3-4 bullets
**Older/Less Relevant Jobs:** 1-3 bullets (or remove if not relevant)

**Each Bullet Must:**
- Be 1-2 lines maximum (no paragraph bullets)
- Start with strong action verb (Led, Developed, Implemented, Managed)
- Include quantified results (numbers, percentages, scale)
- Focus on achievements, NOT responsibilities

## Content Prioritization (AGGRESSIVE REDUCTION)

1. **Remove entirely:** Irrelevant jobs, generic skills, obvious duties
2. **Condense:** Education (degree + dates only), Certifications (name + date)
3. **Prioritize:** Most recent 2-3 relevant positions
4. **Quantify:** Every bullet must have a metric (users, %, time saved, etc.)
5. **Eliminate:** Verbose explanations, adjectives, filler words (the, an, a)
6. **Cut:** Any section that doesn't directly support job qualifications

## 2-Page Resume Formatting (FOR MID/SENIOR LEVEL ONLY - 10+ YEARS)

**If using 2 pages, follow these rules:**

1. **Page Distribution:**
   - **Page 1:** Contact info, Professional Summary, Key Skills, most recent 2-3 jobs (detailed)
   - **Page 2:** Older jobs (condensed 2-3 bullets each), Education, Certifications, optional Projects/Awards

2. **Page Breaks:**
   - DO NOT split a single job description between pages
   - Finish one complete job on page 1, start fresh job on page 2
   - Ensure page 1 ends with complete content (not mid-bullet)

3. **Page 2 Header:**
   - Include: [Name] | [Phone] | [Email] | Page 2
   - Keeps pages connected if separated

4. **Fill Both Pages:**
   - AVOID 1.5-page resumes (looks incomplete)
   - If you can't fill 2 full pages, use 1 page instead
   - Balance white space - don't cram page 1 and leave page 2 sparse

5. **Content Strategy:**
   - Most important content on page 1 (first 30 seconds of review)
   - Older experience gets less detail on page 2
   - Recent jobs: 4-5 bullets | Older jobs: 2-3 bullets

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

## VALIDATION CHECKPOINT

Before considering this resume complete, verify:
- [ ] Total word count is under 400 words (entry-level) or 600 (mid-level) or 800 (senior)
- [ ] No more than 5 blank lines in entire document
- [ ] Skills section uses single-line categories with pipes (|) - NO multi-line categories
- [ ] Education has NO "Relevant Coursework" details
- [ ] Certifications are ONE line each with NO descriptions (just name, issuer, date)
- [ ] Professional Summary is exactly 2-3 sentences (40-60 words)
- [ ] Each job has 3-5 bullets maximum (not more)
- [ ] NO blank lines between skill categories, education entries, or certifications

**If any checkbox is unchecked, the resume is NOT complete. Revise immediately.**

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
        style: Optional[str] = None,
    ) -> str:
        """Create instructions for industry-focused revamp."""
        # Import here to avoid circular dependency
        from ..config.styles import STYLES

        style_guidance = ""
        if style and style in STYLES:
            style_config = STYLES[style]
            style_guidance = f"""
## Style Guidelines

The user has selected the **{style_config['name']}** writing style for their resume.

**Style Characteristics:**
- Tone: {style_config['tone']}
- Approach: {style_config['prompt_guidance']}

**IMPORTANT:** Apply this style consistently throughout the entire enhanced resume. The user has already seen a professional summary preview in this style, so maintain that tone and approach across all sections.

"""

        return f"""# Resume Enhancement Request - Industry Revamp

**Enhancement ID:** `{enhancement_id}`
**Type:** Industry-Focused Revamp
**Industry:** {industry}
**Status:** Pending

{style_guidance}
## Length Requirements (CRITICAL - MUST FOLLOW - 2026 BEST PRACTICES)

**Target Page Length:** Based on 2026 industry research
- Entry-level (0-5 years): **1 PAGE ONLY** (not 2 pages)
- Mid-level (5-10 years): 1-2 pages
- Senior (10+ years): 2 pages MAX

**ABSOLUTE MAXIMUM WORD COUNTS:**
- Entry-level (0-5 years): **400 WORDS MAX** = 1 PAGE ONLY
- Mid-level (5-10 years): **600 WORDS MAX** = 1-2 PAGES
- Senior (10+ years): **800 WORDS MAX** = 2 PAGES (fill both pages)

**CRITICAL:** Count words BEFORE adding markdown syntax. If over limit, CUT content aggressively.

**STRICT LIMITS:**
- NEVER exceed 2 pages regardless of experience
- NEVER exceed word count maximums (400/600/800)
- Entry-level MUST be 1 page (66% of employers require this)
- Minimize white space - use 0.5-0.75" margins if needed
- Line spacing: 1.0-1.15 (single-spaced)

## Formatting Rules (ULTRA-STRICT - ZERO WHITE SPACE TOLERANCE)

❌ **ABSOLUTELY FORBIDDEN:**
- NO decorative dividers (`---` or `===`)
- NO emojis or special characters
- NO blank lines between bullets
- NO blank lines between skill categories
- NO blank lines in Education section
- NO blank lines in Certifications section
- NO custom creative headers
- NO more than 3-4 jobs listed
- NO tables, text boxes, or graphics
- NO "Professional Development" or "Hobbies" sections for entry-level
- NO "Relevant Coursework" expansions in Education
- NO certification descriptions (title and date ONLY)

✅ **STRICT REQUIREMENTS:**
- ONLY 4-5 blank lines in ENTIRE document (one between each major section)
- Contact info: ONE line with pipes (|) separating elements
- Professional Summary: 2-3 sentences (40-60 words MAX), NO blank lines before/after
- Skills: Single-line categories with pipes (see format below), NO multi-line categories
- Each job: Title/Company/Dates, then bullets immediately following
- Education: Degree, University, Location, Dates - ONE line per degree, NO coursework
- Certifications: Name - Issuer | Date - ONE line per cert, NO descriptions
- Lead every bullet with action verb + quantified result

## Skills Section Format (REQUIRED - SINGLE-LINE CATEGORIES)

**WRONG (wastes 8+ lines):**
```
## Skills
**System Administration:** Windows Server, Active Directory...

**Infrastructure & Tools:** Azure, ServiceNow...

**Networking & Security:** TCP/IP, DNS/DHCP...
```

**CORRECT (3-4 lines total with pipe-separated categories):**
```
## Skills
**System Administration:** Windows Server, Active Directory, Microsoft 365, DNS/DHCP, Group Policy | **Infrastructure:** Azure, ServiceNow, Cherwell ITSM, TeamViewer, PowerShell, Virtual Machines | **Networking:** TCP/IP, Network Troubleshooting, Security Compliance | **Technical:** Windows 10/11, Linux, Documentation
```

**Format rules:**
- Maximum 3-4 category groups
- Each category on SAME line, separated by ` | `
- NO blank lines between categories
- Total Skills section: 2-4 lines maximum

## Education & Certifications Format (ULTRA-CONDENSED)

**Education - WRONG:**
```
**Bachelor of Cybersecurity** - Griffith University, Brisbane, QLD | March 2024 - 2026

Relevant Coursework: Applied Network Security, Database Design...
```

**Education - CORRECT:**
```
## Education
**Bachelor of Cybersecurity** - Griffith University, Brisbane, QLD | 2024-2026
**Diploma of Information Technology** - Griffith College, Brisbane, QLD | 2022-2023
```

**Certifications - WRONG:**
```
**IT Support Technical Skills** - Udemy | June 2025

Gained hands-on experience with Active Directory...
```

**Certifications - CORRECT (Name and date ONLY):**
```
## Certifications
IT Support Technical Skills Helpdesk - Udemy | 2025
Computer Systems and Networks - Griffith College | 2023
Advent of Cyber - TryHackMe | 2024
```

**Format rules:**
- ONE line per certification
- NO descriptions or details whatsoever
- NO blank lines between certifications
- Format: `[Certification Name] - [Issuer] | [Year]`

## Bullet Point Guidelines (CRITICAL - VARIES BY JOB)

**Most Recent/Relevant Job:** 4-5 bullets
**Second Most Recent Job:** 3-4 bullets
**Older/Less Relevant Jobs:** 1-3 bullets (or remove if not relevant)

**Each Bullet Must:**
- Be 1-2 lines maximum (no paragraph bullets)
- Start with strong action verb (Led, Developed, Implemented, Managed)
- Include quantified results (numbers, percentages, scale)
- Focus on achievements, NOT responsibilities

## Content Prioritization (AGGRESSIVE REDUCTION)

1. **Remove entirely:** Irrelevant jobs, generic skills, obvious duties
2. **Condense:** Education (degree + dates only), Certifications (name + date)
3. **Prioritize:** Most recent 2-3 relevant positions
4. **Quantify:** Every bullet must have a metric (users, %, time saved, etc.)
5. **Eliminate:** Verbose explanations, adjectives, filler words (the, an, a)
6. **Cut:** Any section that doesn't directly support job qualifications

## 2-Page Resume Formatting (FOR MID/SENIOR LEVEL ONLY - 10+ YEARS)

**If using 2 pages, follow these rules:**

1. **Page Distribution:**
   - **Page 1:** Contact info, Professional Summary, Key Skills, most recent 2-3 jobs (detailed)
   - **Page 2:** Older jobs (condensed 2-3 bullets each), Education, Certifications, optional Projects/Awards

2. **Page Breaks:**
   - DO NOT split a single job description between pages
   - Finish one complete job on page 1, start fresh job on page 2
   - Ensure page 1 ends with complete content (not mid-bullet)

3. **Page 2 Header:**
   - Include: [Name] | [Phone] | [Email] | Page 2
   - Keeps pages connected if separated

4. **Fill Both Pages:**
   - AVOID 1.5-page resumes (looks incomplete)
   - If you can't fill 2 full pages, use 1 page instead
   - Balance white space - don't cram page 1 and leave page 2 sparse

5. **Content Strategy:**
   - Most important content on page 1 (first 30 seconds of review)
   - Older experience gets less detail on page 2
   - Recent jobs: 4-5 bullets | Older jobs: 2-3 bullets

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

    def create_cover_letter_instructions(
        self,
        enhancement_id: str,
        resume_id: str,
        job_id: str,
        enhancement_type: str,
        style: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Create COVER_LETTER_INSTRUCTIONS.md for Claude Code.

        Called AFTER enhanced.md is detected as complete.

        Args:
            enhancement_id: Enhancement ID
            resume_id: Resume ID
            job_id: Job ID (required for cover letters)
            enhancement_type: Type of enhancement
            style: Writing style (same as resume)

        Returns:
            Path to COVER_LETTER_INSTRUCTIONS.md or None if skipped
        """
        enhancement_dir = self.workspace_root / "resumes" / "enhanced" / enhancement_id

        # Only create cover letter for job_tailoring (not industry_revamp)
        if enhancement_type != "job_tailoring" or not job_id:
            logger.info(f"Skipping cover letter for enhancement {enhancement_id} (type: {enhancement_type})")
            return None

        # Check if instructions already exist (avoid duplicates)
        instructions_path = enhancement_dir / "COVER_LETTER_INSTRUCTIONS.md"
        if instructions_path.exists():
            logger.info(f"Cover letter instructions already exist for {enhancement_id}")
            return instructions_path

        instructions = self._create_cover_letter_instructions(
            enhancement_id, resume_id, job_id, style
        )

        with open(instructions_path, "w", encoding="utf-8") as f:
            f.write(instructions)

        logger.info(f"Cover letter instructions created for enhancement {enhancement_id}")
        return instructions_path

    def _create_cover_letter_instructions(
        self,
        enhancement_id: str,
        resume_id: str,
        job_id: str,
        style: Optional[str] = None,
    ) -> str:
        """Create COVER_LETTER_INSTRUCTIONS.md content."""
        from ..config.styles import STYLES

        style_guidance = ""
        if style and style in STYLES:
            style_config = STYLES[style]
            style_guidance = f"""
## Style Guidelines

The user selected the **{style_config['name']}** writing style for their resume.

**CRITICAL:** Use the SAME style for this cover letter to maintain consistency.

**Style Characteristics:**
- Tone: {style_config['tone']}
- Approach: {style_config['prompt_guidance']}

**Important:** The cover letter should feel like a natural companion to the resume.
"""

        return f"""# Cover Letter Generation Request

**Enhancement ID:** `{enhancement_id}`
**Type:** Job-Specific Cover Letter
**Status:** Pending

{style_guidance}
## Task

Generate a professional cover letter tailored to the specific job description.
This cover letter accompanies the enhanced resume in the same directory.

## Input Files

- **Enhanced Resume:** `workspace/resumes/enhanced/{enhancement_id}/enhanced.md`
- **Original Resume:** `workspace/resumes/original/{resume_id}/extracted.txt`
- **Job Description:** `workspace/jobs/{job_id}/description.txt`
- **Job Metadata:** `workspace/jobs/{job_id}/metadata.json`

## Output File

Write the cover letter to:
**`workspace/resumes/enhanced/{enhancement_id}/cover_letter.md`**

## Cover Letter Requirements

### Length & Structure (CRITICAL - HARD LIMIT)
- **ABSOLUTE MAXIMUM:** 200 words total body content
- **Target Range:** 180-200 words (4 paragraphs)
- **NEVER EXCEED 200 words** - will overflow to page 2 by 2+ lines
- **Reason for strict limit:** 262-word cover letters overflow. 200-word limit ensures single-page fit.
- **Opening paragraph:** 35-40 words MAX (2 sentences)
- **Body paragraph 1:** 50-60 words MAX (2-3 sentences)
- **Body paragraph 2:** 50-60 words MAX (2-3 sentences)
- **Closing paragraph:** 30-35 words MAX (1-2 sentences)
- **If at 201+ words:** Delete filler words, combine sentences, use contractions

### Word Reduction Checklist (CRITICAL - USE BEFORE FINALIZING)

**Cut these filler phrases immediately:**
- ❌ "I am writing to express my interest in" → ✅ "I'm interested in"
- ❌ "I have been responsible for" → ✅ "I managed" or "I administered"
- ❌ "Additionally," "Furthermore," "Moreover," → ✅ Delete entirely, start new sentence
- ❌ "in my current position" → ✅ "Currently" or "At [Company]"
- ❌ "while ensuring" → ✅ "ensuring" (delete "while")
- ❌ "that align with your requirements" → ✅ Delete entire phrase
- ❌ "I am particularly attracted to" → ✅ "I'm drawn to" or "This role offers"
- ❌ "I look forward to discussing" → ✅ "I'd welcome discussing"

**Active voice shortcuts:**
- ❌ "I have supported" → ✅ "I supported"
- ❌ "I have assisted with" → ✅ "I assisted with"
- ❌ "positions me to contribute" → ✅ "enables me to contribute"

**Professional Style Adaptation:**
While resume uses formal passive voice, cover letters MUST be CONCISE:
- ✅ Use "I managed" not "I was responsible for managing"
- ✅ Use "I'm" and "I'd" to save words (still professional in 2026)
- ✅ Keep sentences under 20 words each
- ✅ Use periods instead of clauses with "while" or "and"
- ✅ Delete ALL transitional phrases ("Additionally", "Furthermore", "Moreover")

### Content Guidelines
1. **Use ENHANCED resume content** (not original) - reference the improved achievements
2. **Reference specific requirements** from the job description
3. **Highlight 2-3 achievements** that directly relate to the role with metrics
4. **Match terminology** from the job posting
5. **Show company research** - reference something specific about the company or role
6. **Avoid generic phrases** like "I am writing to apply for..."
7. **Start with a compelling hook** that shows enthusiasm and research

### Style Consistency
- Use the **same writing style** as the enhanced resume
- Maintain **consistent tone** and professional level
- Match **vocabulary sophistication** to resume

### Truthfulness
- Only use information **present in the resume**
- Never fabricate achievements or experiences
- Accurately represent skills and qualifications

## Output Format

Use clean markdown:

```markdown
# Cover Letter

[Company Name from job metadata]
[Company Address if available in job description]

Dear Hiring Manager,

[Opening paragraph: 2 sentences]
- State the position and qualifications

[Body paragraph 1: 2-3 sentences]
- Highlight most relevant qualification with metrics
- Connect to job requirement
- Show impact

[Body paragraph 2: 2-3 sentences]
- Highlight second qualification with metrics
- Address another requirement
- Demonstrate value

[Closing paragraph: 1-2 sentences]
- Express interest and thank them

Sincerely,
[Name from resume]
[Email from resume]
[Phone from resume]
```

## VALIDATION CHECKPOINT

Before considering this cover letter complete, COUNT WORDS:
- [ ] Total word count (opening + body1 + body2 + closing) is 180-200 words MAX
- [ ] Opening paragraph: 35-40 words
- [ ] Body paragraph 1: 50-60 words
- [ ] Body paragraph 2: 50-60 words
- [ ] Closing paragraph: 30-35 words
- [ ] Has 4 paragraphs (opening + 2 body + closing)
- [ ] Includes 2-3 quantified achievements from resume
- [ ] References specific job requirements
- [ ] NO paragraph uses "Additionally" or "Furthermore"
- [ ] NO passive constructions like "I have been responsible for"
- [ ] ALL sentences are under 20 words
- [ ] Tone matches resume writing style
- [ ] Contact information matches resume

**If word count exceeds 200, CUT content immediately. This is non-negotiable.**

## Examples of Strong Openings

❌ **Avoid:** "I am writing to apply for the Software Engineer position..."

✅ **Good:** "As a senior developer who has scaled microservices to handle 10M+ daily requests, I'm excited about the opportunity to bring my cloud architecture expertise to [Company]'s platform engineering team."

✅ **Good:** "Your company's recent launch of [Product] and commitment to [Value] aligns perfectly with my 8-year background in building customer-centric SaaS solutions that increase retention by 35%."

## When Complete

After writing `cover_letter.md`, the backend will:
1. Detect the file exists
2. Update cover_letter_status to "completed"
3. Make it available for download alongside resume

---

**Created:** {datetime.utcnow().isoformat()}
"""

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

    def delete_resume(self, resume_id: str) -> bool:
        """
        Delete a resume and its files from the workspace.

        Args:
            resume_id: Resume ID to delete

        Returns:
            True if deleted successfully, False if not found
        """
        resume_dir = self.workspace_root / "resumes" / "original" / resume_id

        if not resume_dir.exists():
            logger.warning(f"Resume directory not found: {resume_id}")
            return False

        try:
            shutil.rmtree(resume_dir)
            logger.info(f"Resume deleted from workspace: {resume_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete resume {resume_id}: {e}")
            raise

    def delete_all_resumes(self) -> Tuple[int, int]:
        """
        Delete all resumes from the workspace.

        Returns:
            Tuple of (original_count, enhanced_count) - number of directories deleted
        """
        original_dir = self.workspace_root / "resumes" / "original"
        enhanced_dir = self.workspace_root / "resumes" / "enhanced"

        original_count = 0
        enhanced_count = 0

        # Delete original resumes
        if original_dir.exists():
            original_count = len(list(original_dir.iterdir()))
            shutil.rmtree(original_dir)
            original_dir.mkdir(parents=True, exist_ok=True)

        # Delete enhanced resumes
        if enhanced_dir.exists():
            enhanced_count = len(list(enhanced_dir.iterdir()))
            shutil.rmtree(enhanced_dir)
            enhanced_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Deleted all resumes: {original_count} original, {enhanced_count} enhanced")
        return original_count, enhanced_count

    def delete_enhancement(self, enhancement_id: str) -> bool:
        """
        Delete an enhancement and its files from the workspace.

        Args:
            enhancement_id: Enhancement ID to delete

        Returns:
            True if deleted successfully, False if not found
        """
        enhancement_dir = self.workspace_root / "resumes" / "enhanced" / enhancement_id

        if not enhancement_dir.exists():
            logger.warning(f"Enhancement directory not found: {enhancement_id}")
            return False

        try:
            shutil.rmtree(enhancement_dir)
            logger.info(f"Enhancement deleted from workspace: {enhancement_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete enhancement {enhancement_id}: {e}")
            raise

    def delete_all_enhancements(self) -> int:
        """
        Delete all enhancements from the workspace.

        Returns:
            Number of enhancement directories deleted
        """
        enhanced_dir = self.workspace_root / "resumes" / "enhanced"

        count = 0
        if enhanced_dir.exists():
            count = len(list(enhanced_dir.iterdir()))
            shutil.rmtree(enhanced_dir)
            enhanced_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Deleted all enhancements: {count} directories")
        return count

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job and its files from the workspace.

        Args:
            job_id: Job ID to delete

        Returns:
            True if deleted successfully, False if not found
        """
        job_dir = self.workspace_root / "jobs" / job_id

        if not job_dir.exists():
            logger.warning(f"Job directory not found: {job_id}")
            return False

        try:
            shutil.rmtree(job_dir)
            logger.info(f"Job deleted from workspace: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            raise

    def delete_all_jobs(self) -> int:
        """
        Delete all jobs from the workspace.

        Returns:
            Number of job directories deleted
        """
        jobs_dir = self.workspace_root / "jobs"

        count = 0
        if jobs_dir.exists():
            count = len(list(jobs_dir.iterdir()))
            shutil.rmtree(jobs_dir)
            jobs_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Deleted all jobs: {count} directories")
        return count
