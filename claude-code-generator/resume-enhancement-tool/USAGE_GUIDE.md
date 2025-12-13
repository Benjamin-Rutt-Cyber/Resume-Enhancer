# Resume Enhancement Tool - Usage Guide

## Overview

This is a single-user web application that helps you enhance your resume using Claude Code. The application provides two powerful features:

1. **Job-Specific Tailoring** - Match your resume to specific job descriptions
2. **Industry-Focused Revamp** - Comprehensive resume overhaul for target industries

**Key Advantage:** No API calls needed! Claude Code reads files directly from the workspace and generates enhanced resumes.

## How It Works

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Web UI     │─────▶│  Workspace   │◀─────│ Claude Code │
│ (Organize)  │      │   (Files)    │      │  (Enhance)  │
└─────────────┘      └──────────────┘      └─────────────┘
      │                      │                      │
      │                      │                      │
   Upload              INSTRUCTIONS.md         enhanced.md
   Resume              + resume.txt            (markdown)
   Job Desc                                         │
      │                      │                      │
      └──────────────────────┴──────────────────────┘
                             │
                        PDF Output
```

## Workflow

### Step 1: Upload Resume (Web UI)

1. Open web UI: `http://localhost:3000`
2. Navigate to "Resumes" page
3. Upload your resume (PDF or DOCX format)
4. Backend parses the file and extracts text
5. Files stored in: `workspace/resumes/original/{resume_id}/`

**What happens:**
- Original file saved as `source.pdf` or `source.docx`
- Text extracted and saved as `extracted.txt` (for Claude Code to read)
- Metadata saved in `metadata.json`

### Step 2: Add Job Description (Web UI)

#### Option A: For Job Tailoring
1. Navigate to "Jobs" page
2. Paste or upload job description
3. Add job title and company (optional)
4. Click "Save"
5. Files stored in: `workspace/jobs/{job_id}/`

#### Option B: For Industry Revamp
Skip this step - you'll specify the industry when creating the enhancement.

### Step 3: Create Enhancement Request (Web UI)

1. Navigate to "Enhancements" page
2. Click "New Enhancement"
3. Select:
   - Resume to enhance
   - Enhancement type:
     - **Job Tailoring:** Match to specific job
     - **Industry Revamp:** Comprehensive overhaul for industry
4. If Job Tailoring: Select job description
5. If Industry Revamp: Select industry (IT, Cybersecurity, Finance, etc.)
6. Click "Create"

**What happens:**
- Backend creates enhancement workspace: `workspace/resumes/enhanced/{enhancement_id}/`
- Creates `INSTRUCTIONS.md` telling Claude Code what to do
- Creates `metadata.json` with enhancement details
- Status set to "pending"

### Step 4: Enhance with Claude Code

**Now switch to Claude Code!**

#### For Job Tailoring:

```bash
# Run the tailor-resume command
/tailor-resume

# Or if you know the enhancement ID:
/tailor-resume abc-123-def

# Claude Code will:
# 1. Find pending job-tailoring requests
# 2. Read INSTRUCTIONS.md
# 3. Read your resume (extracted.txt)
# 4. Read job description
# 5. Generate enhanced resume optimized for the job
# 6. Write to workspace/resumes/enhanced/{id}/enhanced.md
```

#### For Industry Revamp:

```bash
# Run the revamp-for-industry command
/revamp-for-industry

# Or if you know the enhancement ID:
/revamp-for-industry xyz-789-abc

# Claude Code will:
# 1. Find pending industry-revamp requests
# 2. Read INSTRUCTIONS.md
# 3. Read your resume (extracted.txt)
# 4. Read industry guide
# 5. Comprehensively revamp resume for the industry
# 6. Write to workspace/resumes/enhanced/{id}/enhanced.md
```

**What Claude Code does:**
- Uses the `resume-enhancement-agent` for expert guidance
- Reads your resume and job/industry requirements
- Generates enhanced resume as markdown
- Applies resume best practices:
  - Keyword optimization
  - Quantified achievements
  - Action verbs
  - ATS-friendly formatting
  - Industry-specific terminology

### Step 5: Finalize and Download (Web UI)

**Return to the Web UI!**

1. Navigate to "Enhancements" page
2. You'll see the enhancement status changed to "Ready"
3. Click "Finalize"
4. Backend converts markdown → PDF using WeasyPrint
5. Click "Download" to get your enhanced PDF resume

**What happens:**
- Backend detects `enhanced.md` file
- Converts markdown to PDF using HTML template
- Saves as `enhanced.pdf`
- Status changed to "completed"
- PDF ready for download

## Available Industries

The following industry guides are available:

- **IT (Information Technology)** - Software development, DevOps, Cloud, etc.
- **Cybersecurity** - Security engineering, SOC, penetration testing, etc.
- **Finance** - Financial analysis, accounting, investment, etc.

More industries can be added by creating new guide files in:
`workspace/_instructions/industries/`

## Claude Code Components

### Custom Agent

**`resume-enhancement-agent`**
- Expert in resume optimization
- Knows resume best practices
- Applies job-matching and industry-specific techniques
- Never fabricates information

### Custom Commands

**`/tailor-resume`**
- Quick job-specific tailoring
- Matches keywords from job description
- Highlights relevant experience
- 5-10 minute enhancement

**`/revamp-for-industry`**
- Comprehensive industry revamp
- Full restructure for industry standards
- Industry-specific terminology
- 15-30 minute transformation

### Industry Guides

Located in: `workspace/_instructions/industries/`

Each guide contains:
- Industry-specific resume structure
- Key terminology and keywords
- Important certifications
- Formatting conventions
- Best practices and examples

## File Structure

```
resume-enhancement-tool/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── models/            # Database models
│   │   ├── utils/             # Document parser, PDF generator
│   │   └── services/          # Workspace service
│   └── requirements.txt
│
├── frontend/                   # React frontend
│   └── src/
│
├── workspace/                  # File storage (Claude Code reads/writes here)
│   ├── resumes/
│   │   ├── original/          # Uploaded resumes
│   │   └── enhanced/          # Enhanced versions
│   ├── jobs/                  # Job descriptions
│   ├── templates/             # PDF templates
│   └── _instructions/         # Industry guides
│
└── .claude/                    # Claude Code integration
    ├── agents/                 # resume-enhancement-agent
    └── commands/               # /tailor-resume, /revamp-for-industry
```

## Tips for Best Results

### Uploading Resumes
- Use well-formatted PDFs or DOCX files
- Ensure text is selectable (not scanned images)
- Include all relevant experience and achievements

### Job Descriptions
- Copy the complete job description
- Include requirements, responsibilities, and qualifications
- The more detail, the better the matching

### Job Tailoring
- Best for applying to specific positions
- Quick turnaround (5-10 minutes)
- Focuses on keyword matching and relevance

### Industry Revamp
- Best for career transitions or rebranding
- More comprehensive (15-30 minutes)
- Restructures entire resume for industry standards
- Use when targeting a new industry

### Working with Claude Code
- Let Claude Code finish completely before checking results
- Review the enhanced markdown before finalizing to PDF
- You can manually edit `enhanced.md` if needed before finalizing

## Troubleshooting

### Resume upload fails
- Check file format (PDF or DOCX only)
- Ensure file isn't password protected
- Try a different PDF/DOCX if extraction fails

### No text extracted from PDF
- PDF might be scanned images (no actual text)
- Try using OCR software first
- Or manually type/paste resume content

### Claude Code doesn't find pending enhancements
- Check that Web UI created the enhancement
- Look for INSTRUCTIONS.md in workspace/resumes/enhanced/
- Try running command with specific enhancement ID

### PDF generation fails
- Check that enhanced.md was created
- Verify markdown syntax is valid
- Check backend logs for errors

### Enhanced resume looks wrong
- Review the markdown file in workspace
- Edit manually if needed
- Re-finalize to regenerate PDF

## Next Steps

After generating your project, you'll need to:

1. **Set up database:**
   ```bash
   cd backend
   # Update DATABASE_URL in .env
   alembic upgrade head
   ```

2. **Start backend:**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

3. **Start frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Use Claude Code:**
   - Open project in Claude Code
   - Upload resume via web UI
   - Use `/tailor-resume` or `/revamp-for-industry`
   - Finalize and download

## Support

For issues or questions:
- Check INSTRUCTIONS.md files in workspace
- Review industry guides in workspace/_instructions/industries/
- Check backend logs for errors
- Verify file permissions in workspace directory

---

**Happy resume enhancing! 🚀**
