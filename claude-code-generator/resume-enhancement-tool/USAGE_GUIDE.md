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

### Step 1.5: Select Your Writing Style ✨ OPTIMIZED (Zero API Costs)

**Immediately after upload**, you'll see 5 predefined writing style options:

1. **Professional** - Traditional corporate tone with formal language
2. **Executive** - Senior leadership language with strategic focus
3. **Technical** - Detailed technical terminology, metrics-driven
4. **Creative** - Dynamic, personality-focused, engaging language
5. **Concise** - Brief impactful statements (maximum brevity)

**How it works:**
- Frontend displays static style options with clear descriptions
- NO API calls - instant selection (eliminated ~$3/month in costs)
- Each style includes tone description and industry recommendations
- Select the style that best matches your target role and personality
- Your selected style will be applied to all enhancements of this resume

**What happens:**
- Selected style saved to Resume record in database (single API call to save selection)
- Style guidance will be included in INSTRUCTIONS.md for Claude Code
- Enhanced resume will use your selected writing style consistently

**Tips:**
- **Professional**: Best for corporate jobs, traditional industries (Banking, Healthcare)
- **Executive**: Best for C-suite, VP, Director level positions
- **Technical**: Best for engineering, data science, technical specialist roles
- **Creative**: Best for marketing, design, product management, startup roles
- **Concise**: Best for senior roles where brevity matters, scanning-heavy positions

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

### Step 4.5: Cover Letter Auto-Generation ✨ OPTIMIZED

**Automatic process - no action required!**

After Claude Code generates the enhanced resume:
- Backend automatically triggers cover letter generation
- Cover letter is generated following the same writing style as resume
- **Exactly 1 page** (185-205 words, 4 paragraphs)
- Professional structure:
  - Opening: State position and qualifications (2 sentences)
  - Body 1: Primary qualification with metrics (2-3 sentences)
  - Body 2: Secondary qualification with metrics (2-3 sentences)
  - Closing: Express interest and thanks (1-2 sentences)

**What happens:**
- System detects `enhanced.md` completion
- Reads job description and enhanced resume
- Generates tailored cover letter in markdown
- Saves to `workspace/resumes/enhanced/{id}/cover_letter.md`
- Status updated to "completed" for both resume and cover letter

**Quality Guarantees:**
- ✅ No overflow to page 2
- ✅ No excessive white space
- ✅ Accounts for formatting overhead (company address, salutation, signature)
- ✅ Consistent tone with selected writing style
- ✅ Only uses information from resume (no fabrication)

### Step 5: Finalize and Download (Web UI)

**Return to the Web UI!**

1. Navigate to "Enhancements" page
2. You'll see the enhancement status changed to "completed"
3. Download options available:
   - **Download Resume (Markdown)** - Enhanced resume in markdown format
   - **Download Resume (DOCX)** - Enhanced resume as Word document
   - **Download Cover Letter (Markdown)** - 1-page cover letter
   - **Download Cover Letter (DOCX)** - Cover letter as Word document

**What happens:**
- Backend detects both `enhanced.md` and `cover_letter.md` files
- Status changed to "completed" for both
- All download formats available immediately
- DOCX files generated on-demand with proper formatting

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

1. **Set up environment:**
   ```bash
   cd backend
   # Create .env file
   cp .env.example .env

   # NOTE: ANTHROPIC_API_KEY is NOT required
   # Style preview API has been disabled to eliminate costs
   # The application uses static style selection (zero API costs)

   # Set your SECRET_KEY (required)
   echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
   ```

2. **Set up database:**
   ```bash
   cd backend
   # Update DATABASE_URL in .env if needed
   alembic upgrade head
   ```

3. **Install dependencies:**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd ../frontend
   npm install
   ```

4. **Start backend:**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

5. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

6. **Use Claude Code:**
   - Open project in Claude Code
   - Upload resume via web UI
   - Select writing style
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
