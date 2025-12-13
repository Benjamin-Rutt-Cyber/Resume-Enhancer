---
name: revamp-for-industry
description: Comprehensive resume revamp for a specific industry
---

# Revamp Resume for Industry

Perform a comprehensive, in-depth revamp of a resume for a specific industry (IT, Cybersecurity, Finance, etc.).

## Usage

```
/revamp-for-industry [enhancement_id]
```

Or discover pending industry revamps automatically:
```
/revamp-for-industry
```

## What This Command Does

1. **Discovers pending industry-revamp requests** in the workspace
2. **Reads the enhancement instructions** and industry guide
3. **Activates the resume-enhancement-agent** for comprehensive revamp
4. **Generates a fully restructured resume** optimized for the target industry

## Process

### Step 1: Find Pending Industry Revamps

```bash
# Look for pending industry-revamp enhancements
find workspace/resumes/enhanced -name "INSTRUCTIONS.md" -type f
```

Filter for `industry_revamp` type enhancements that don't have `enhanced.md` yet.

### Step 2: Read Industry Guide

Read the industry-specific guide:
```
workspace/_instructions/industries/{industry}.md
```

Industry guides contain:
- Industry-specific resume structure
- Key terminology and keywords
- Important certifications and skills
- Formatting conventions
- Best practices

### Step 3: Comprehensive Revamp

Use the resume-enhancement-agent to:
1. Read the original resume
2. Read the industry guide thoroughly
3. **Comprehensively restructure** the resume:
   - Reorder sections for industry standards
   - Emphasize relevant experience
   - Use industry-specific terminology
   - Highlight relevant certifications
   - Apply industry formatting conventions
4. Generate a polished, industry-optimized resume

### Step 4: Write Output

Write the revamped resume as markdown to:
```
workspace/resumes/enhanced/{enhancement_id}/enhanced.md
```

## Industry Guides Available

- **IT (Information Technology):** `it.md`
- **Cybersecurity:** `cybersecurity.md`
- **Finance:** `finance.md`
- **Marketing:** `marketing.md`
- **Healthcare:** `healthcare.md`

## Difference from Job Tailoring

| Aspect | Job Tailoring | Industry Revamp |
|--------|---------------|-----------------|
| Scope | Specific job posting | Entire industry |
| Depth | Targeted adjustments | Comprehensive restructure |
| Focus | Match keywords | Industry best practices |
| Structure | Minor tweaks | Full reorganization |
| Time | Quick (5-10 min) | Thorough (15-30 min) |

## Example Workflow

```bash
# User runs command
/revamp-for-industry

# System finds pending enhancement
Found pending enhancement: xyz-789-abc
Type: industry_revamp
Industry: Cybersecurity
Resume: workspace/resumes/original/resume-456/extracted.txt
Guide: workspace/_instructions/industries/cybersecurity.md

# Read files
Reading resume...
Reading Cybersecurity industry guide...

# Analyze industry requirements
Industry requirements for Cybersecurity:
- Security skills section at top
- Certifications prominently displayed
- Incident response experience
- Compliance frameworks mentioned
- Security tools and platforms
- Risk assessment experience

# Comprehensively revamp
Restructuring resume for Cybersecurity industry...
- Moving security skills to top
- Emphasizing security certifications (CISSP, CEH)
- Rewriting experience bullets to focus on security
- Adding security-specific terminology
- Highlighting relevant tools (Splunk, Nessus, etc.)

# Write revamped version
Writing revamped resume to:
workspace/resumes/enhanced/xyz-789-abc/enhanced.md

✓ Complete! Resume fully optimized for Cybersecurity industry.
User can now finalize in web UI to generate PDF.
```

## Industry-Specific Tips

### IT/Software Development
- Lead with technical skills matrix
- Include GitHub/portfolio links
- Mention programming languages and frameworks
- Highlight system architecture work
- Include cloud platforms (AWS, Azure, GCP)

### Cybersecurity
- Security certifications first
- Mention security frameworks (NIST, ISO 27001)
- Highlight threat detection/response
- Include security tools expertise
- Emphasize compliance knowledge

### Finance
- Quantify financial impact (ROI, cost savings)
- Mention financial systems/software
- Highlight analytical capabilities
- Include relevant certifications (CFA, CPA)
- Emphasize regulatory knowledge

### Marketing
- Lead with metrics and results
- Include campaign performance data
- Mention marketing tools/platforms
- Highlight growth percentages
- Show content strategy experience

## After Completion

Once you've written `enhanced.md`:
1. The web UI will detect the new file
2. User clicks "Finalize" to convert to PDF
3. Backend converts markdown → PDF using WeasyPrint
4. User downloads the industry-optimized resume

## Quality Checklist

Before marking complete, ensure:
- [ ] Resume structure matches industry standards
- [ ] Industry-specific terminology is used
- [ ] Relevant skills are prominently displayed
- [ ] Experience is reframed for industry context
- [ ] Certifications are highlighted (if applicable)
- [ ] Format follows industry conventions
- [ ] Content remains truthful (no fabrication)
- [ ] ATS-friendly formatting maintained

## Related

- See `resume-enhancement-agent.md` for detailed enhancement guidelines
- See `/tailor-resume` for quick job-specific tailoring
- See `workspace/_instructions/industries/` for all industry guides

---

**Ready to revamp resumes for any industry! Use this command for comprehensive, industry-focused resume transformations.**
