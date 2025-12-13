---
name: tailor-resume
description: Tailor a resume for a specific job posting
---

# Tailor Resume for Job

Tailor an existing resume to match a specific job description.

## Usage

```
/tailor-resume [enhancement_id]
```

Or discover pending enhancements automatically:
```
/tailor-resume
```

## What This Command Does

1. **Discovers pending job-tailoring requests** in the workspace
2. **Reads the enhancement instructions** from INSTRUCTIONS.md
3. **Activates the resume-enhancement-agent** to perform the tailoring
4. **Generates an enhanced resume** optimized for the specific job

## Process

### Step 1: Find Pending Enhancements

```bash
# Look for pending job-tailoring enhancements
find workspace/resumes/enhanced -name "INSTRUCTIONS.md" -type f
```

### Step 2: Read Instructions

For each INSTRUCTIONS.md file found:
- Check if it's a job_tailoring type
- Check if enhanced.md already exists (skip if completed)
- Note the resume_id and job_id

### Step 3: Perform Enhancement

Use the resume-enhancement-agent to:
1. Read the original resume
2. Read the job description
3. Generate enhanced resume with:
   - Matched keywords from job posting
   - Highlighted relevant experience
   - Quantified achievements
   - ATS-friendly formatting

### Step 4: Write Output

Write the enhanced resume as markdown to:
```
workspace/resumes/enhanced/{enhancement_id}/enhanced.md
```

## Example Workflow

```bash
# User runs command
/tailor-resume

# System finds pending enhancement
Found pending enhancement: abc-123-def
Type: job_tailoring
Resume: workspace/resumes/original/resume-456/extracted.txt
Job: workspace/jobs/job-789/description.txt

# Read files
Reading resume...
Reading job description...

# Analyze and enhance
Job requirements detected:
- Python, FastAPI, PostgreSQL
- 5+ years experience
- Team leadership
- Cloud deployment (AWS/Azure)

Enhancing resume to match...

# Write enhanced version
Writing enhanced resume to:
workspace/resumes/enhanced/abc-123-def/enhanced.md

✓ Complete! User can now finalize in web UI to generate PDF.
```

## Tips for Best Results

1. **Read Carefully:** Pay attention to job requirements and keywords
2. **Match Skills:** Emphasize skills that appear in job description
3. **Quantify:** Add metrics to achievements when possible
4. **Stay Truthful:** Never fabricate experiences
5. **ATS-Friendly:** Use standard markdown formatting

## After Completion

Once you've written `enhanced.md`:
1. The web UI will detect the new file
2. User clicks "Finalize" to convert to PDF
3. Backend converts markdown → PDF using WeasyPrint
4. User downloads the tailored resume

## Related

- See `resume-enhancement-agent.md` for detailed enhancement guidelines
- See `/revamp-for-industry` for comprehensive industry-focused revamps
- See `workspace/_instructions/` for industry guides

---

**Ready to tailor some resumes! Use this command whenever you need to match a resume to a job posting.**
