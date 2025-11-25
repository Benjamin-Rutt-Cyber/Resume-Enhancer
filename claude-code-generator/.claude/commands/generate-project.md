---
name: generate-project
description: Generate a new Claude Code project structure interactively
---

# Generate New Claude Code Project

Generate a complete Claude Code project environment with agents, skills, commands, and boilerplate code.

## Interactive Mode

This command will:
1. Ask you about your project (name, type, tech stack, features)
2. Generate the complete project structure
3. Create all necessary files (.claude/, documentation, boilerplate)

## Steps

1. **Gather Project Information**
   - Ask the user for project details interactively
   - Validate inputs

2. **Invoke the Generator**
   - Run the claude-gen CLI tool with the collected information
   - Handle both installed and development modes

3. **Report Results**
   - Show what was generated
   - Display next steps

## Implementation

First, check if claude-gen is installed:

```bash
if command -v claude-gen &> /dev/null; then
    echo "✓ claude-gen is installed"
    CLAUDE_GEN="claude-gen"
else
    # Fall back to running from source
    echo "Running from source..."
    CLAUDE_GEN="python -m src.cli.main"
fi
```

Then run interactively:

```bash
cd /path/to/output/directory
$CLAUDE_GEN init --interactive
```

## Alternative: Quick Generation

If the user provides all details upfront, generate directly:

```bash
claude-gen init \
  --project "Project Name" \
  --type saas-web-app \
  --backend python-fastapi \
  --frontend react-typescript \
  --database postgresql \
  --output ./new-project \
  --no-interactive
```

## After Generation

1. Navigate to the generated project: `cd project-name`
2. Review the generated `.claude/` directory
3. Run the setup command: `/setup-dev`
4. Start building with Claude Code!

## Usage Examples

**Example 1: Full Interactive Mode**
```
User: /generate-project
Assistant: I'll help you generate a new Claude Code project. Let me gather some information...
[Runs interactive prompts]
[Generates project]
Assistant: ✅ Project generated at ./my-saas-app/
```

**Example 2: Quick Generation**
```
User: /generate-project SaaS API with FastAPI and React
Assistant: I'll generate a SaaS web application with FastAPI backend and React frontend...
[Generates project]
Assistant: ✅ Complete! Check ./saas-api/ for your new project.
```

## Troubleshooting

**If claude-gen is not installed:**
```bash
pip install claude-code-generator
# Or install in development mode
cd /path/to/claude-code-generator
pip install -e .
```

**If running from source:**
```bash
cd /path/to/claude-code-generator
python -m src.cli.main init --interactive
```
