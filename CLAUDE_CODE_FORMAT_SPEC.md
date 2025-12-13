# Claude Code Format Specification - Complete Reference

**Last Updated:** 2025-11-15
**Based on:** Official Claude Code Documentation (2025)

---

## Table of Contents

1. [Overview](#overview)
2. [Subagents (Agents)](#subagents-agents)
3. [Skills](#skills)
4. [Slash Commands](#slash-commands)
5. [Plugins](#plugins)
6. [Directory Structure](#directory-structure)
7. [Invocation Mechanisms](#invocation-mechanisms)
8. [Best Practices](#best-practices)

---

## Overview

Claude Code supports four main extensibility mechanisms:

| Type | Purpose | Invocation | Complexity | File Extension |
|------|---------|------------|------------|----------------|
| **Subagents** | Specialized AI assistants with separate context | Auto or Manual | Medium | `.md` |
| **Skills** | Reusable capabilities with scripts/resources | Auto (tool call) | High | `SKILL.md` |
| **Slash Commands** | Quick prompt snippets | Manual (`/command`) | Low | `.md` |
| **Plugins** | Packaged collections of above | N/A | High | `plugin.json` |

---

## Subagents (Agents)

### What Are Subagents?

Subagents are specialized AI assistants with:
- **Separate context window** (isolated from main conversation)
- **Custom system prompts** (specific expertise)
- **Configurable tool access** (restricted capabilities)
- **Model selection** (can use different Claude models)

### File Format

```markdown
---
name: agent-name
description: Natural language description of when and why to use this agent
tools: Tool1, Tool2, Tool3
model: sonnet
---

System prompt describing the agent's expertise, behavior, and specific
instructions for problem-solving approaches.

## Agent Role

Clear definition of expertise area and responsibilities.

## Instructions

Step-by-step procedures for task execution.

## Constraints

Specific limitations and guidelines.

## Expected Output

Format and quality criteria for deliverables.
```

### YAML Frontmatter Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | ✅ Yes | string | Unique identifier (lowercase, hyphens only) |
| `description` | ✅ Yes | string | Natural language description of purpose and when to invoke |
| `tools` | ❌ No | string | Comma-separated tool list (omit to inherit all tools) |
| `model` | ❌ No | string | Model alias: `sonnet`, `opus`, `haiku`, or `inherit` |

### Storage Locations

**Priority Order (highest to lowest):**

1. **Project-level**: `.claude/agents/*.md`
   - Shared with team via git
   - Highest priority
   - Project-specific agents

2. **User-level**: `~/.claude/agents/*.md`
   - Available across all projects
   - Personal workflow agents

3. **Plugin agents**: `<plugin-root>/agents/*.md`
   - Installed via plugins
   - Lowest priority

### Invocation Methods

**1. Automatic Delegation**
- Claude analyzes the `description` field
- Matches user requests to appropriate agent
- Automatically invokes when task matches

**Pro Tip:** Include "use PROACTIVELY" in description for more automatic triggering

**2. Explicit/Manual Invocation**
```
User: "Use the code-reviewer agent to check my recent changes"
User: "Have the debugger agent investigate this error"
```

**3. Task Tool (Programmatic)**
```xml
<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <subagent_type>code-reviewer</subagent_type>
    <prompt>Review the authentication module for security issues</prompt>
  </parameters>
</tool_use>
```

### Example: Complete Agent File

```markdown
---
name: security-audit-agent
description: Use this agent PROACTIVELY when reviewing code for security vulnerabilities, checking authentication flows, validating input sanitization, or conducting OWASP Top 10 audits. This agent specializes in identifying security issues before they reach production.
tools: Read, Grep, Bash
model: opus
---

# Security Audit Agent

You are an elite security researcher and penetration testing expert specializing in application security audits.

## Your Mission

Conduct thorough security reviews of code, identifying vulnerabilities across the OWASP Top 10 and beyond. Provide actionable remediation guidance with code examples.

## Review Checklist

### Authentication & Authorization
- [ ] Password hashing (bcrypt, argon2)
- [ ] JWT token validation
- [ ] Session management
- [ ] OAuth implementation
- [ ] Authorization checks on all endpoints

### Input Validation
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] Command injection prevention
- [ ] Path traversal protection
- [ ] File upload validation

### Sensitive Data
- [ ] No secrets in code
- [ ] Encrypted data at rest
- [ ] HTTPS enforcement
- [ ] Secure cookie flags
- [ ] API key rotation

## Output Format

Generate a security audit report with:

1. **Executive Summary** (severity distribution)
2. **Critical Issues** (immediate action required)
3. **High Priority Issues** (fix before production)
4. **Medium/Low Issues** (technical debt)
5. **Recommendations** (security improvements)

For each issue provide:
- **Severity:** Critical/High/Medium/Low
- **Location:** File path and line numbers
- **Description:** What the vulnerability is
- **Impact:** Potential security consequences
- **Remediation:** Specific code fix with examples

## Standards

- Follow OWASP ASVS guidelines
- Reference CWE numbers for vulnerabilities
- Provide CVSS scores for critical issues
- Include compliance implications (GDPR, SOC2, etc.)
```

---

## Skills

### What Are Skills?

Skills are reusable capabilities that:
- **Package instructions with resources** (scripts, templates, reference docs)
- **Auto-invoke based on context** (Claude detects relevance)
- **Inject specialized knowledge** (extend Claude's abilities)
- **Include executable code** (helper scripts in any language)

### File Structure

Skills are **directories** containing:

```
skill-name/
├── SKILL.md          # Required: Main instructions with frontmatter
├── reference.md      # Optional: Additional documentation
├── examples/         # Optional: Usage examples
├── scripts/          # Optional: Helper scripts
│   ├── extract.py
│   └── process.sh
└── templates/        # Optional: File templates
    └── output.json.template
```

### SKILL.md Format

```markdown
---
name: skill-identifier
description: What the skill does and when Claude should use it
allowed-tools: [Tool1, Tool2]
---

# Skill Title

## Overview

Brief description of skill capabilities.

## When to Use This Skill

Specific scenarios where this skill applies.

## Instructions

Step-by-step guidance for Claude to follow.

## Available Resources

- `scripts/extract.py` - Extracts data from files
- `templates/output.json.template` - Standard output format
- `reference.md` - Detailed API documentation

## Examples

### Example 1: Basic Usage

Input: ...
Process: ...
Output: ...

## Best Practices

- Guideline 1
- Guideline 2
```

### YAML Frontmatter Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | ✅ Yes | string | Lowercase letters, numbers, hyphens only (max 64 chars) |
| `description` | ✅ Yes | string | Explains functionality and activation triggers (max 1024 chars) |
| `allowed-tools` | ❌ No | array | Restricts tools Claude can use when skill is active |

**Critical:** The `description` field determines when Claude invokes the skill. Make it detailed and include trigger keywords.

### Storage Locations

**Three sources (priority order):**

1. **Personal Skills**: `~/.claude/skills/skill-name/`
   - Available across all projects
   - Individual workflows
   - Git-ignored

2. **Project Skills**: `.claude/skills/skill-name/`
   - Shared with team via git
   - Team conventions and standards
   - Version controlled

3. **Plugin Skills**: `<plugin-root>/skills/skill-name/`
   - Installed via plugins
   - Community-shared capabilities

### Invocation Mechanism

Skills use a **tool call/tool response** mechanism:

**Step 1: Tool Call**
```xml
<tool_use>
  <tool_name>Skill</tool_name>
  <parameters>
    <skill>pdf</skill>
  </parameters>
</tool_use>
```

**Step 2: Tool Response**
```xml
<tool_result>
  Base path: ~/.claude/skills/pdf/

  [Full contents of SKILL.md including frontmatter and instructions]
</tool_result>
```

**Step 3: Execution**
- Claude reads the expanded instructions
- Has access to all bundled scripts/resources
- Can reference files using base path
- Executes within main conversation context

### Key Differences from Agents

| Aspect | Skills | Agents |
|--------|--------|--------|
| **Context** | Main conversation | Separate subprocess |
| **Structure** | Directory with resources | Single .md file |
| **Invocation** | Tool call (automatic) | Task delegation |
| **Complexity** | Complex workflows | Specialized prompts |
| **Resources** | Scripts, templates, docs | Just system prompt |

### Example: Complete Skill

**Directory Structure:**
```
.claude/skills/api-security-scanner/
├── SKILL.md
├── reference.md
├── scripts/
│   ├── scan_endpoints.py
│   └── check_auth.py
└── checklists/
    └── owasp_api_top10.md
```

**SKILL.md:**
```markdown
---
name: api-security-scanner
description: Use this skill when scanning REST APIs for security vulnerabilities, checking OWASP API Top 10 issues, validating authentication mechanisms, or auditing API endpoints for common security flaws. Automatically invoked when user mentions API security, vulnerability scanning, or endpoint testing.
allowed-tools: [Bash, Read, Write, Grep]
---

# API Security Scanner Skill

## Overview

Comprehensive API security scanning capability with automated vulnerability detection across OWASP API Security Top 10.

## Available Tools

### Scripts

1. **scripts/scan_endpoints.py**
   - Discovers API endpoints from OpenAPI specs
   - Tests for common vulnerabilities
   - Usage: `python scripts/scan_endpoints.py <spec-file>`

2. **scripts/check_auth.py**
   - Validates authentication mechanisms
   - Tests for broken authentication
   - Usage: `python scripts/check_auth.py <base-url>`

### Reference Materials

- **checklists/owasp_api_top10.md** - Complete OWASP API Security checklist

## Scanning Procedure

### Phase 1: Discovery
1. Read OpenAPI/Swagger specification
2. Run `scan_endpoints.py` to map all endpoints
3. Identify authentication requirements
4. Document API structure

### Phase 2: Authentication Testing
1. Run `check_auth.py` for each auth mechanism
2. Test for:
   - Broken authentication (A1)
   - Broken authorization (A2)
   - JWT vulnerabilities
   - Session management issues

### Phase 3: Input Validation
Test each endpoint for:
- SQL injection
- NoSQL injection
- Command injection
- Path traversal
- Mass assignment
- Excessive data exposure (A3)

### Phase 4: Security Misconfiguration
Check for:
- Missing security headers
- CORS misconfigurations
- Rate limiting gaps (A4)
- Verbose error messages

### Phase 5: Reporting
Generate comprehensive report with:
- Executive summary
- Vulnerability details (severity, location, remediation)
- OWASP API Top 10 coverage
- Recommended fixes with code examples

## Output Format

```json
{
  "scan_date": "2025-11-15",
  "api_endpoint": "https://api.example.com",
  "total_endpoints": 45,
  "vulnerabilities": {
    "critical": 2,
    "high": 5,
    "medium": 12,
    "low": 3
  },
  "findings": [...]
}
```

## Best Practices

- Always test in non-production environments
- Document all findings with remediation steps
- Retest after fixes applied
- Generate executive and technical reports
```

---

## Slash Commands

### What Are Slash Commands?

Slash commands are:
- **Quick prompt shortcuts** (frequently-used instructions)
- **Single Markdown files** (simple structure)
- **Manually invoked** (user types `/command`)
- **Argument support** (pass parameters)

### File Format

```markdown
---
allowed-tools: [Bash, Read, Write]
description: Brief command summary
argument-hint: [expected format]
model: sonnet
disable-model-invocation: false
---

Full prompt text that Claude will execute.

You can use $ARGUMENTS to capture passed values.
Use $1, $2, etc. for positional arguments.

## Example

User runs: /command arg1 arg2
- $ARGUMENTS becomes: "arg1 arg2"
- $1 becomes: "arg1"
- $2 becomes: "arg2"
```

### YAML Frontmatter Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `allowed-tools` | array | (inherit) | Tools available during command execution |
| `description` | string | (first line) | Brief command summary |
| `argument-hint` | string | none | Expected argument format (shown in UI) |
| `model` | string | (inherit) | Specific model to use |
| `disable-model-invocation` | boolean | false | Prevents command from using SlashCommand tool |

### Storage Locations

**Two scopes:**

1. **Project commands**: `.claude/commands/*.md`
   - Shared with team
   - Project-specific workflows

2. **Personal commands**: `~/.claude/commands/*.md`
   - Available across all projects
   - Individual shortcuts

### Namespace Organization

Use subdirectories to organize without affecting command names:

```
.claude/commands/
├── frontend/
│   ├── component.md    → /component (shows: "project:frontend")
│   └── test.md         → /test (shows: "project:frontend")
├── backend/
│   └── migrate.md      → /migrate (shows: "project:backend")
└── deploy.md           → /deploy
```

### Argument Usage

**Global Arguments ($ARGUMENTS):**
```markdown
---
description: Fix issue following coding standards
argument-hint: <issue-number>
---

Fix issue #$ARGUMENTS following our coding standards.

1. Read the issue details
2. Implement the fix
3. Add tests
4. Update documentation
```

**Usage:** `/fix-issue 123` → `$ARGUMENTS = "123"`

**Positional Arguments ($1, $2, ...):**
```markdown
---
description: Create a new component
argument-hint: <component-name> <component-type>
---

Create a new $2 component named $1:

1. Create file: src/components/$1.tsx
2. Implement $2 component logic
3. Add tests
4. Export from index
```

**Usage:** `/create-component Header functional`
- `$1 = "Header"`
- `$2 = "functional"`

### Advanced Features

**1. Bash Execution (! prefix)**
```markdown
---
description: Show git status
---

!git status
!git diff --stat
```

**2. File References (@ prefix)**
```markdown
---
description: Review file with context
argument-hint: <file-path>
---

Review the file @$ARGUMENTS against our coding standards.
```

**3. Extended Thinking**
Include keywords to trigger deeper analysis:
```markdown
---
description: Architectural design review
---

<thinking>
Analyze the architectural decisions in this codebase...
</thinking>
```

### Example: Complete Slash Command

**.claude/commands/security-scan.md:**
```markdown
---
allowed-tools: [Bash, Read, Grep, Write]
description: Run comprehensive security scan on the project
argument-hint: [--quick|--full]
model: opus
---

# Security Scan

Run a comprehensive security audit of the codebase.

Mode: $ARGUMENTS

## Scan Procedure

### 1. Secret Detection
Search for exposed secrets:
- API keys
- Passwords
- Private keys
- Tokens
- Database credentials

### 2. Dependency Vulnerabilities
Check for known vulnerabilities in dependencies:
- Run `npm audit` or `pip-audit`
- Review outdated packages
- Check for security advisories

### 3. Code Analysis
Analyze code for:
- SQL injection risks
- XSS vulnerabilities
- Command injection
- Path traversal
- Insecure deserialization

### 4. Configuration Review
Check security configurations:
- HTTPS enforcement
- CORS settings
- Security headers
- Authentication mechanisms
- Rate limiting

### 5. Generate Report
Create detailed security report:
- Executive summary
- Critical findings
- Recommendations
- Remediation steps

Save report to: `security-audit-${date}.md`
```

**Usage:**
```
/security-scan --full
/security-scan --quick
```

---

## Plugins

### What Are Plugins?

Plugins are **packaged collections** of:
- Slash commands
- Subagents
- Skills
- Hooks (post-execution behaviors)
- MCP servers (Model Context Protocol integrations)

### Plugin Structure

```
my-plugin/
├── plugin.json                 # Required: Manifest
├── README.md                   # Recommended: Documentation
├── LICENSE                     # Recommended: License info
├── commands/                   # Optional: Slash commands
│   ├── deploy.md
│   └── test.md
├── agents/                     # Optional: Subagents
│   ├── reviewer.md
│   └── tester.md
├── skills/                     # Optional: Skills
│   └── security-scan/
│       ├── SKILL.md
│       └── scripts/
├── hooks/                      # Optional: Hooks
│   └── pre-commit.sh
└── servers/                    # Optional: MCP servers
    └── custom-server/
```

### plugin.json Manifest

```json
{
  "name": "my-awesome-plugin",
  "version": "1.0.0",
  "description": "Comprehensive development toolkit",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "homepage": "https://github.com/username/my-plugin",
  "repository": "https://github.com/username/my-plugin",
  "license": "MIT",
  "keywords": ["security", "testing", "deployment"],
  "tags": ["development", "devops"],

  "commands": ["commands"],
  "agents": ["agents"],
  "skills": ["skills"],

  "hooks": {
    "post-tool-use": {
      "matcher": "tool.name == 'Write'",
      "command": "/format-code"
    }
  },

  "mcpServers": {
    "custom-server": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/custom-server/run.sh",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"]
    }
  }
}
```

### Manifest Fields

**Core Metadata:**

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | ✅ Yes | string | Plugin identifier (kebab-case) |
| `version` | ✅ Yes | string | Semantic version (e.g., "1.0.0") |
| `description` | ❌ No | string | Brief plugin description |
| `author` | ❌ No | object | Author info: `{name, email, url}` |
| `homepage` | ❌ No | string | Documentation URL |
| `repository` | ❌ No | string | Source code repository URL |
| `license` | ❌ No | string | SPDX license identifier |
| `keywords` | ❌ No | array | Search/discovery keywords |
| `tags` | ❌ No | array | Categorization tags |

**Component Configuration:**

| Field | Type | Description |
|-------|------|-------------|
| `commands` | string or array | Path(s) to command files/directories |
| `agents` | string or array | Path(s) to agent files/directories |
| `skills` | string or array | Path(s) to skill directories |
| `hooks` | object | Hook configurations |
| `mcpServers` | object | MCP server configurations |

**Environment Variable:**
- `${CLAUDE_PLUGIN_ROOT}` - Resolves to plugin installation directory

### Marketplace Structure

**marketplace.json:**
```json
{
  "name": "my-marketplace",
  "owner": {
    "name": "Marketplace Owner",
    "email": "owner@example.com"
  },
  "metadata": {
    "description": "Curated collection of Claude Code plugins",
    "version": "1.0.0",
    "pluginRoot": "https://raw.githubusercontent.com/user/repo/main/"
  },
  "plugins": [
    {
      "name": "security-suite",
      "version": "2.1.0",
      "description": "Comprehensive security tools",
      "author": {"name": "Security Team"},
      "source": "plugins/security-suite",
      "category": "security",
      "tags": ["security", "audit", "testing"],
      "strict": true
    },
    {
      "name": "devops-toolkit",
      "version": "1.5.0",
      "description": "DevOps automation tools",
      "source": "github:username/devops-plugin",
      "category": "devops",
      "tags": ["deployment", "ci-cd", "docker"]
    }
  ]
}
```

### Marketplace Fields

**Required:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Marketplace identifier |
| `owner` | object | Owner info: `{name, email}` |
| `plugins` | array | List of plugin entries |

**Optional Metadata:**

| Field | Type | Description |
|-------|------|-------------|
| `metadata.description` | string | Marketplace description |
| `metadata.version` | string | Marketplace version |
| `metadata.pluginRoot` | string | Base path for relative sources |

**Plugin Entry Fields:**

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | ✅ Yes | string | Plugin identifier |
| `source` | ✅ Yes | string | Where to fetch (path, GitHub, git URL) |
| `version` | ❌ No | string | Plugin version |
| `description` | ❌ No | string | Brief description |
| `category` | ❌ No | string | Category for organization |
| `tags` | ❌ No | array | Searchable tags |
| `strict` | ❌ No | boolean | Requires plugin.json (default: true) |

**Source Format Examples:**
- Relative path: `"plugins/security-suite"`
- GitHub: `"github:username/repo"` or `"github:username/repo/subdir"`
- Git URL: `"https://github.com/user/repo.git"`
- Direct URL: `"https://example.com/plugin.zip"`

### Distribution & Installation

**Hosting a Marketplace:**

1. Create `marketplace.json` in git repository
2. Commit and push to GitHub (or any git host)
3. Users add with: `/plugin marketplace add username/repo`

**Installing Plugins:**

```bash
# Add marketplace
/plugin marketplace add username/repo

# Browse marketplace
/plugin

# Install plugin
/plugin install plugin-name@marketplace-name

# Update plugin
/plugin update plugin-name

# Remove plugin
/plugin remove plugin-name
```

**Team Distribution:**

Configure automatic marketplace in `.claude/settings.json`:
```json
{
  "extraKnownMarketplaces": [
    {
      "source": "github:company/internal-plugins"
    },
    {
      "source": "https://plugins.example.com/marketplace.json"
    }
  ]
}
```

---

## Directory Structure

### Complete Project Structure

```
project-root/
├── .claude/
│   ├── agents/                    # Project subagents
│   │   ├── api-agent.md
│   │   ├── frontend-agent.md
│   │   └── security-agent.md
│   ├── skills/                    # Project skills
│   │   ├── api-testing/
│   │   │   ├── SKILL.md
│   │   │   ├── scripts/
│   │   │   └── templates/
│   │   └── deployment/
│   │       ├── SKILL.md
│   │       └── workflows/
│   ├── commands/                  # Project slash commands
│   │   ├── frontend/
│   │   │   ├── component.md
│   │   │   └── test.md
│   │   ├── backend/
│   │   │   ├── api.md
│   │   │   └── migrate.md
│   │   └── deploy.md
│   ├── settings.json              # Project settings
│   └── plugins/                   # Installed plugins (auto-managed)
│       └── security-suite/
├── .claude-plugin/                # If this project IS a plugin
│   └── marketplace.json
└── plugin.json                    # If this project IS a plugin

~/.claude/                         # User-level (personal)
├── agents/                        # Personal agents
│   └── my-workflow-agent.md
├── skills/                        # Personal skills
│   └── my-skill/
│       └── SKILL.md
└── commands/                      # Personal commands
    └── my-command.md
```

### Priority Resolution

When multiple files have the same name, Claude Code uses this priority:

1. **Project-level** (`.claude/`) - Highest priority
2. **User-level** (`~/.claude/`) - Medium priority
3. **Plugin-level** (plugin installations) - Lowest priority

---

## Invocation Mechanisms

### How Components Are Triggered

| Component | Trigger | Mechanism | Context |
|-----------|---------|-----------|---------|
| **Subagents** | Auto or Manual | Task delegation | Separate subprocess |
| **Skills** | Auto | Tool call (Skill tool) | Main conversation |
| **Slash Commands** | Manual only | User types `/cmd` | Main conversation |
| **Plugins** | N/A | Container for above | N/A |

### Subagent Invocation Flow

```
User Request
    ↓
Claude analyzes request
    ↓
Matches against agent descriptions
    ↓
┌─────────────────────────┐
│ Task tool invocation    │
│ - Agent name            │
│ - Task description      │
│ - Model selection       │
└─────────────────────────┘
    ↓
New subprocess created
    ↓
Agent system prompt loaded
    ↓
Tool access restricted (if configured)
    ↓
Agent executes task
    ↓
Returns result to main conversation
```

### Skill Invocation Flow

```
User Request
    ↓
Claude analyzes request
    ↓
Matches against skill descriptions
    ↓
┌─────────────────────────┐
│ Skill tool call         │
│ <skill>skill-name</skill>│
└─────────────────────────┘
    ↓
Tool response with SKILL.md content
    ↓
Skill instructions injected into context
    ↓
Claude follows skill instructions
    ↓
Can execute bundled scripts
    ↓
Continues in main conversation
```

### Slash Command Invocation Flow

```
User types: /command arg1 arg2
    ↓
Command file loaded from .claude/commands/
    ↓
Frontmatter processed
    ↓
Arguments substituted
    ↓
Prompt expanded
    ↓
Claude executes in main conversation
    ↓
Uses configured tools and model
```

---

## Best Practices

### Subagents (Agents)

✅ **Do:**
- Create agents with **single, clear responsibilities**
- Write **detailed descriptions** with trigger phrases
- Include **specific step-by-step instructions**
- Add "use PROACTIVELY" for automatic triggering
- Restrict tools to minimum necessary
- Provide **quality checklists** in agent prompt
- Version control project agents (.claude/agents/)

❌ **Don't:**
- Create one agent that does everything
- Write vague descriptions
- Assume Claude knows your domain
- Grant unnecessary tool access
- Forget to test agent invocation

### Skills

✅ **Do:**
- Package **related capabilities together** (instructions + scripts)
- Write **comprehensive, detailed descriptions** (max 1024 chars)
- Include **concrete examples** in SKILL.md
- Document all bundled scripts and their usage
- Use **progressive disclosure** (reference.md for details)
- Test scripts independently before bundling
- Use `allowed-tools` to restrict capabilities

❌ **Don't:**
- Create skills for simple one-liners (use commands instead)
- Write brief, cryptic descriptions
- Bundle unrelated capabilities
- Forget to document script dependencies
- Include broken or untested scripts

### Slash Commands

✅ **Do:**
- Use for **frequently-repeated prompts**
- Provide clear `argument-hint` in frontmatter
- Use `$ARGUMENTS` and `$1, $2` appropriately
- Organize with subdirectories for namespacing
- Keep commands focused and simple
- Test with various argument combinations

❌ **Don't:**
- Create commands for complex multi-step workflows (use agents/skills)
- Forget to handle missing arguments gracefully
- Make commands too generic
- Overcomplicate simple shortcuts

### Plugins

✅ **Do:**
- Create cohesive, **themed collections**
- Write comprehensive README.md
- Include LICENSE file
- Version properly (semantic versioning)
- Test all components work together
- Provide clear installation instructions
- Use `${CLAUDE_PLUGIN_ROOT}` for paths

❌ **Don't:**
- Bundle unrelated components
- Forget to update version on changes
- Assume users know how to use plugin
- Hard-code absolute paths
- Skip testing before publishing

### General Guidelines

**Naming Conventions:**
- Use `kebab-case` for all identifiers
- Be descriptive but concise
- Avoid special characters except hyphens
- Max 64 characters for names

**Descriptions:**
- Front-load important keywords
- Mention specific use cases
- Include trigger phrases
- Be specific about capabilities
- Skills: max 1024 characters

**Organization:**
- Group related items in subdirectories
- Use consistent naming across project
- Document team conventions
- Keep project vs personal separate

**Testing:**
- Test invocation (auto and manual)
- Verify tool access restrictions
- Check argument handling
- Validate cross-platform compatibility
- Test with different models (sonnet/opus/haiku)

**Documentation:**
- Include usage examples
- Document all parameters
- Explain edge cases
- Provide troubleshooting tips
- Keep docs up-to-date

---

## Quick Reference

### File Extension Summary

| Type | Extension | Required File | Location |
|------|-----------|---------------|----------|
| Subagent | `.md` | `agent-name.md` | `.claude/agents/` or `~/.claude/agents/` |
| Skill | N/A (dir) | `SKILL.md` | `.claude/skills/skill-name/` |
| Slash Command | `.md` | `command.md` | `.claude/commands/` or `~/.claude/commands/` |
| Plugin | N/A (dir) | `plugin.json` | Plugin directory |

### Frontmatter Field Summary

| Field | Agents | Skills | Commands | Required |
|-------|--------|--------|----------|----------|
| `name` | ✅ | ✅ | ❌ | Yes (agents/skills) |
| `description` | ✅ | ✅ | ❌ | Yes (agents/skills) |
| `tools` | ✅ | ❌ | ❌ | No |
| `allowed-tools` | ❌ | ✅ | ✅ | No |
| `model` | ✅ | ❌ | ✅ | No |
| `argument-hint` | ❌ | ❌ | ✅ | No |
| `disable-model-invocation` | ❌ | ❌ | ✅ | No |

### CLI Commands

```bash
# Agents
/agents                          # Manage agents
/agents create                   # Create new agent
/agents list                     # List all agents

# Skills
# (No CLI, managed via files)

# Commands
# (Auto-discovered from .claude/commands/)

# Plugins
/plugin                          # Browse plugins
/plugin marketplace add <repo>   # Add marketplace
/plugin install <name>           # Install plugin
/plugin update <name>            # Update plugin
/plugin remove <name>            # Remove plugin
/plugin list                     # List installed

# Settings
/settings                        # Open settings
```

---

## Additional Resources

**Official Documentation:**
- Subagents: https://code.claude.com/docs/en/sub-agents
- Skills: https://code.claude.com/docs/en/skills
- Slash Commands: https://code.claude.com/docs/en/slash-commands
- Plugins: https://code.claude.com/docs/en/plugin-marketplaces

**Community Resources:**
- Awesome Claude Code: https://github.com/hesreallyhim/awesome-claude-code
- Claude Code Subagents: https://github.com/VoltAgent/awesome-claude-code-subagents
- Commands Collection: https://github.com/wshobson/commands

**Best Practices:**
- Anthropic Engineering Blog: https://www.anthropic.com/engineering/claude-code-best-practices
- Skills Deep Dive: https://mikhail.io/2025/10/claude-code-skills/

---

**End of Specification**
