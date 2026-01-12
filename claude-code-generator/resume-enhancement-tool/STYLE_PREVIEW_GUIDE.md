# Manual Style Preview Generation Guide

This guide explains how to generate style previews using Claude Code (your subscription) instead of requiring a separate Anthropic API key.

## How It Works

Instead of the backend automatically calling the Anthropic API, **you ask Claude Code in this chat** to generate the style previews for you. This uses your existing Claude Code subscription!

## Workflow

### Step 1: Upload Resume
1. Go to http://localhost:3002
2. Upload your resume (PDF or DOCX)
3. You'll see the style preview modal appear with a loading message

### Step 2: Generate Previews with Claude Code
1. **Come back to this Claude Code chat**
2. Say: **"Generate style previews for my latest resume"** or **"Generate style previews for resume ID: [resume-id]"**
3. Claude Code will:
   - Read your resume from the workspace
   - Generate 5 different Professional Summary versions (one for each style)
   - Save them to the workspace
   - Update the database

### Step 3: View and Select Style
1. **Return to the web app** (http://localhost:3002)
2. Refresh or click "Retry" if needed
3. You'll see all 5 style previews
4. Select your preferred writing style
5. Continue with adding jobs and creating enhancements

## The 5 Writing Styles

1. **Professional** - Traditional corporate tone with formal language
2. **Executive** - Senior leadership language with strategic focus
3. **Technical** - Detailed technical terminology with specific metrics
4. **Creative** - Dynamic personality-focused with engaging language
5. **Concise** - Brief impactful statements (max 10 words per bullet)

## Example Commands

```
"Generate style previews for my resume"
"Create style previews for the most recent resume"
"Generate previews for resume ID: 6ac9c386-c265-4640-8764-fd463a559462"
```

## Technical Details

**Storage Location:**
```
workspace/resumes/original/{resume-id}/style_previews/
├── professional.txt
├── executive.txt
├── technical.txt
├── creative.txt
└── concise.txt
```

**Database Update:**
- Sets `style_previews_generated = True` on the Resume record

## Benefits

✅ **No API Key Required** - Uses your Claude Code subscription
✅ **Same Quality** - Claude Code generates the same high-quality previews
✅ **More Control** - You decide when to generate previews
✅ **Cost-Free** - No additional API charges beyond your subscription

## Notes

- Preview generation takes about 30 seconds with Claude Code
- You can regenerate previews anytime by running the command again
- The frontend will show a "loading" state until previews are generated
- Make sure both backend and frontend servers are running
