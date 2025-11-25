# Claude Code Generator

**Instantly scaffold complete Claude Code project environments from natural language descriptions.**

Generate specialized agents, reusable skills, custom commands, documentation, and boilerplate code for any project type—all optimized for Claude Code.

## 🎯 Dual-Use Design

Use the generator in two ways:

### 1️⃣ Standalone CLI Tool (Primary)

```bash
# Interactive mode
claude-gen init

# One-liner
claude-gen init --project "API Security Platform" --type saas-web-app

# Let Claude analyze your description
claude-gen init --description "Build a real-time chat app with WebSockets" --analyze
```

### 2️⃣ From Within Claude Code (Integrated)

```
# Use slash command
/generate-project

# Or just ask naturally
"Create a new SaaS application for task management"

# project-generator-agent activates automatically
```

**Both modes generate the same complete project structure.**

## ✨ What Gets Generated

```
your-project/
├── .claude/
│   ├── agents/              # Specialized AI assistants
│   │   ├── api-development-agent.md
│   │   ├── frontend-ui-agent.md
│   │   ├── database-agent.md
│   │   ├── security-agent.md
│   │   └── testing-agent.md
│   ├── skills/              # Reusable knowledge
│   │   ├── python-fastapi/
│   │   ├── react-typescript/
│   │   ├── postgresql/
│   │   └── authentication/
│   └── commands/            # Workflow automation
│       ├── setup-dev.md
│       ├── run-tests.md
│       └── deploy.md
├── src/                     # Boilerplate code
│   ├── backend/
│   └── frontend/
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DATABASE_SCHEMA.md
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Installation

```bash
# From PyPI (when published)
pip install claude-code-generator

# From source (development)
git clone https://github.com/yourusername/claude-code-generator.git
cd claude-code-generator
pip install -e .
```

### Generate Your First Project

**Interactive Mode (Recommended):**
```bash
claude-gen init --interactive
```

**Quick Generation:**
```bash
claude-gen init \
  --project "My SaaS App" \
  --type saas-web-app \
  --backend python-fastapi \
  --frontend react-typescript \
  --database postgresql \
  --features authentication,payments \
  --no-interactive
```

**AI-Powered Analysis:**
```bash
claude-gen init \
  --description "A cybersecurity platform for API testing with automated vulnerability scanning" \
  --analyze
```

### Use from Claude Code

1. Open any directory in Claude Code
2. Run: `/generate-project`
3. Or ask: *"Create a new mobile app project with React Native"*
4. The project-generator-agent handles the rest!

## 📦 Supported Project Types

| Type | Description | Command |
|------|-------------|---------|
| **SaaS Web App** | Full-stack application with auth, payments, APIs | `--type saas-web-app` |
| **API Service** | RESTful API or microservice backend | `--type api-service` |
| **Hardware/IoT** | Embedded systems, firmware, IoT devices | `--type hardware-iot` |
| **Mobile App** | React Native, Flutter, native apps | `--type mobile-app` |
| **Data Science** | ML/AI projects with Jupyter notebooks | `--type data-science` |

## 🤖 Reusable Agent Library

The generator includes a curated library of **comprehensive, battle-tested agents** (1000-1500+ lines each) that are copied as-is to your project:

- **api-development-agent** (1500+ lines) - REST API development across all frameworks
- **testing-agent** (1400+ lines) - TDD, unit/integration/E2E testing
- **deployment-agent** (1200+ lines) - Docker, CI/CD, Kubernetes, cloud deployment

These agents are **reusable across all projects**—no templating needed, just pure expertise.

## 🎓 Usage from Claude Code

The generator includes native Claude Code integration:

**Slash Command:** `/generate-project`
- Runs the CLI interactively
- Works in both installed and development modes

**Agent:** `project-generator-agent`
- Activates on "create a project", "generate a [type] app", etc.
- Invokes CLI via Bash tool
- Provides guidance and next steps

## 🎯 Project Status

**Version**: 0.2.0
**Status**: Production-Ready ✅
**Architecture Rating**: 8/10 - GOOD

### Recent Updates (2025-11-25)
- ✅ All enhancements completed (--yes, interactive mode, PATH setup)
- ✅ Architecture review completed (see ARCHITECTURE_REVIEW.md)
- ✅ Tested and working: Generated 48-file SaaS project successfully
- ⚠️ Next: Add test suite (high priority)

### Quality Metrics
- **Lines of Code**: 2,908 Python
- **Test Coverage**: 0% (target: 80%)
- **Agents**: 7 development agents, 47 plugin catalog entries
- **Project Types**: 5 comprehensive configurations

## 📚 Documentation

- **[ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md)** - Comprehensive architecture review (NEW!)
- **[ENHANCEMENTS.md](ENHANCEMENTS.md)** - All completed enhancements (NEW!)
- **[USAGE.md](USAGE.md)** - Complete usage guide with PATH troubleshooting
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project architecture
- **[AGENT_LIBRARY_DESIGN.md](AGENT_LIBRARY_DESIGN.md)** - Reusable agent design

## 📄 License

MIT License - see LICENSE for details.

---

**Made with ❤️ for the Claude Code community**

Start generating amazing projects: `claude-gen init` or `/generate-project` in Claude Code
