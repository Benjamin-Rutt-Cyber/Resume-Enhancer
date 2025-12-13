# Resume Enhancement Request - Job Tailoring

**Enhancement ID:** `278e8683-1933-4dc1-b41b-5c96582f102c`
**Type:** Job-Specific Tailoring
**Status:** Pending

## Task

Tailor the provided resume to match the specific job description. Focus on:
- Matching keywords from the job description
- Highlighting relevant experience and skills
- Quantifying achievements where possible
- Keeping the resume ATS-friendly

## Input Files

- **Resume:** `workspace/resumes/original/c842b7b6-cf5c-4344-a12d-5387cc740649/extracted.txt`
- **Job Description:** `workspace/jobs/a8a3e3ad-4084-4d04-aa42-95c694713f58/description.txt`

## Output File

Write the enhanced resume to:
**`workspace/resumes/enhanced/278e8683-1933-4dc1-b41b-5c96582f102c/enhanced.md`**

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

**Created:** 2025-12-13T14:59:13.002265
