# Claude Code Generator - Usage Guide

Complete guide for using the Claude Code Generator as both a standalone CLI tool and from within Claude Code.

## 📦 Installation

### Option 1: Install from PyPI (When Published)

```bash
pip install claude-code-generator
```

### Option 2: Install from Source (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-code-generator.git
cd claude-code-generator

# Install in development mode
pip install -e .

# Verify installation
claude-gen --version
```

### Option 3: Use Without Installation

```bash
# Run directly from source
cd claude-code-generator
python -m src.cli.main --help
```

### Fixing PATH Issues (Windows)

If you get "claude-gen: command not found" after installation:

**Quick Fix (PowerShell - Recommended):**
```powershell
cd claude-code-generator
.\setup-path.ps1
```

**Manual Fix:**
1. Open "Environment Variables" in Windows Settings
2. Edit user PATH variable
3. Add: `C:\Users\YourUsername\AppData\Roaming\Python\Python3XX\Scripts`
4. Click OK and restart terminal

**Temporary Workaround:**
```bash
# Always works without PATH setup
python -m src.cli.main --help
python -m src.cli.main init --interactive
```

### Fixing PATH Issues (Linux/Mac)

If you get "claude-gen: command not found":

**Quick Fix (Bash/Zsh - Recommended):**
```bash
cd claude-code-generator
chmod +x setup-path.sh
./setup-path.sh
source ~/.bashrc  # or source ~/.zshrc
```

**Manual Fix:**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

**Temporary Workaround:**
```bash
# Always works without PATH setup
python3 -m src.cli.main --help
python3 -m src.cli.main init --interactive
```

## 🚀 Usage Mode 1: Standalone CLI Tool

### Interactive Mode (Recommended for First-Time Users)

Launch an interactive session with beautiful prompts that guide you through project creation:

```bash
claude-gen init --interactive
# or just
claude-gen init
# (automatically switches to interactive if project/description not provided)
```

This will show a guided wizard that prompts you for:
- Project name
- Project description (detailed)
- Project type with descriptions (SaaS, API, mobile, IoT, data science)
- Option to auto-detect project type with AI
- Whether to generate starter code/boilerplate
- Automatic confirmation (no extra prompts)

**Example Session:**
```
🎯 Claude Code Project Generator

What are you building?
> A cybersecurity API testing platform

What type of project is this?
> API/Backend Service

Choose your backend framework:
> Python/FastAPI

Choose your database:
> PostgreSQL

Select features to include:
☑ Authentication (JWT/OAuth)
☑ API documentation (OpenAPI)
☑ Security scanning
☐ Payment processing (Stripe)

Generate project structure? [Y/n] y

✨ Generating your Claude Code environment...

✅ Created .claude/agents/
   - api-development-agent.md
   - security-scanning-agent.md
   - testing-agent.md
   - deployment-agent.md
   - database-agent.md

✅ Created .claude/skills/
   - python-fastapi/
   - postgresql/
   - authentication-jwt/
   - api-security/

✅ Created .claude/commands/
   - setup-dev.md
   - run-tests.md
   - db-migrate.md
   - security-scan.md

✅ Created documentation/
   - ARCHITECTURE.md
   - API.md
   - DATABASE_SCHEMA.md
   - SECURITY.md

🎉 Project environment ready!

Next steps:
1. cd api-security-testing-platform
2. Review .claude/agents/ to see available agents
3. Run: /setup-dev to initialize development environment
4. Start building with Claude Code!
```

### Non-Interactive Mode (For Automation)

When you know exactly what you want, provide all parameters:

```bash
claude-gen init \
  --project "My SaaS Platform" \
  --description "A real-time collaboration tool" \
  --type saas-web-app \
  --output ./my-saas-platform \
  --yes
```

**Key Flags:**
- `--yes` or `-y`: Skip confirmation prompts (auto-accept)
- `--no-ai`: Use keyword-based detection instead of Claude API
- `--with-code`: Generate starter code/boilerplate
- `--overwrite`: Overwrite existing files without asking

**Full Automation Example:**
```bash
# Perfect for CI/CD or scripts
claude-gen init \
  --project "API Service" \
  --description "REST API with authentication and database" \
  --type api-service \
  --yes \
  --no-ai \
  --with-code \
  --output ./api-service
```

### Using Claude API for Analysis

Let Claude analyze your description and determine the best configuration:

```bash
claude-gen init \
  --description "Build a real-time chat application with message history, user authentication, file sharing, and group channels" \
  --analyze \
  --api-key $ANTHROPIC_API_KEY
```

The tool will:
1. Send your description to Claude API
2. Extract project type, tech stack, features, and requirements
3. Generate appropriate agents and skills
4. Create the complete project structure

### Command Reference

```bash
# Show help
claude-gen --help
claude-gen init --help

# Show version
claude-gen --version

# List available templates
claude-gen list
claude-gen list --agents
claude-gen list --skills
claude-gen list --project-types

# Validate a project configuration
claude-gen validate --config project-config.yaml

# Add a template to the library
claude-gen add-template --type agent --name my-custom-agent

# Test the generator
claude-gen test --output ./test-output
```

### Advanced Options

```bash
# Specify custom output directory
claude-gen init --output ~/projects/my-app

# Skip certain components
claude-gen init --skip-frontend --skip-docs

# Include specific agents only
claude-gen init --agents api-development,database,testing

# Use custom template variables
claude-gen init --custom "company_name=Acme Inc" --custom "license=MIT"

# Force overwrite existing directory
claude-gen init --output ./existing-project --force

# Merge with existing project
claude-gen init --output ./existing-project --merge

# Generate with verbose output
claude-gen init --verbose

# Quiet mode (minimal output)
claude-gen init --quiet

# JSON output (for programmatic use)
claude-gen init --output-json
```

## 🤖 Usage Mode 2: From Within Claude Code

### Method 1: Slash Command

Use the `/generate-project` command in any Claude Code session:

```
/generate-project
```

This launches the interactive generator and guides you through project creation.

**Example:**
```
You: /generate-project

Claude: I'll help you generate a new Claude Code project. The tool will ask you some questions about your project.

[Runs: claude-gen init --interactive]

Claude: ✅ Your project has been generated!

📁 my-saas-app/
├── .claude/agents/      (5 agents created)
├── .claude/skills/      (4 skills added)
├── .claude/commands/    (6 commands available)
├── src/backend/
├── src/frontend/
└── docs/

Next steps:
1. cd my-saas-app
2. Run /setup-dev to initialize
3. Start building!
```

### Method 2: Natural Language (Proactive Agent)

Just ask Claude Code to create a project naturally:

```
You: "I want to create a new SaaS application for API testing"

Claude: I'll help you create a SaaS application for API testing! Let me generate a complete Claude Code project structure for you...

[project-generator-agent activates and runs claude-gen]

Claude: ✅ I've generated your API testing SaaS project with:

**Agents:**
- api-development-agent (FastAPI specialist)
- security-scanning-agent (vulnerability detection)
- frontend-ui-agent (React + TypeScript)
- database-agent (PostgreSQL)
- testing-agent (pytest + E2E)

**Skills:**
- python-fastapi
- react-typescript
- postgresql
- api-security
- authentication-jwt

**Commands:**
- /setup-dev - Initialize development environment
- /run-tests - Execute test suite
- /security-scan - Run security audit
- /deploy - Deploy to staging/production

Your project is ready at ./api-testing-saas/

Would you like me to:
1. Walk you through the generated structure?
2. Run the setup command?
3. Start building a specific feature?
```

### Method 3: Ask for Specific Project Types

```
You: "Generate a mobile app project with React Native"

Claude: [Uses project-generator-agent to create mobile app structure]

You: "Create an IoT firmware project for Raspberry Pi Pico"

Claude: [Generates hardware/IoT project with embedded agents]

You: "Scaffold a data science project with Jupyter notebooks"

Claude: [Creates data science project with ML/AI agents]
```

## 🎯 Project Types

### 1. SaaS Web Application

Full-stack web application with subscription model.

**Command:**
```bash
claude-gen init --type saas-web-app
```

**Generated:**
- API development agent
- Frontend UI agent
- Database agent
- Authentication agent
- Payment processing agent (if requested)
- Testing agent
- Deployment agent

### 2. API/Backend Service

RESTful API or backend microservice.

**Command:**
```bash
claude-gen init --type api-service
```

**Generated:**
- API development agent
- Database agent
- Security audit agent
- API documentation agent
- Testing agent
- Deployment agent

### 3. Hardware/IoT Device

Embedded systems or IoT devices.

**Command:**
```bash
claude-gen init --type hardware-iot
```

**Generated:**
- Firmware development agent
- Hardware IoT agent
- Sensor integration agent
- MQTT/networking agent
- Testing agent
- Mobile companion app agent (optional)

### 4. Mobile Application

React Native, Flutter, or native mobile apps.

**Command:**
```bash
claude-gen init --type mobile-app
```

**Generated:**
- Mobile app agent
- API integration agent
- State management agent
- UI/UX agent
- Testing agent
- Deployment agent

### 5. Data Science Project

ML/AI and data analysis projects.

**Command:**
```bash
claude-gen init --type data-science
```

**Generated:**
- Data science agent
- Model training agent
- Data preprocessing agent
- Visualization agent
- Jupyter notebook templates
- Experiment tracking

## 📚 Examples

### Example 1: Quick SaaS Project

```bash
claude-gen init \
  --project "TaskManager Pro" \
  --type saas-web-app \
  --backend python-fastapi \
  --frontend nextjs \
  --database postgresql \
  --features authentication,payments \
  --no-interactive
```

### Example 2: Microservice API

```bash
claude-gen init \
  --project "Payment Processing Service" \
  --type api-service \
  --backend node-express \
  --database mongodb \
  --features authentication,rate-limiting,api-docs \
  --no-interactive
```

### Example 3: IoT Device

```bash
claude-gen init \
  --project "Smart Thermostat" \
  --type hardware-iot \
  --platform raspberry-pi-pico \
  --features mqtt,sensors,mobile-app \
  --no-interactive
```

### Example 4: Let Claude Decide

```bash
claude-gen init \
  --description "A real-time multiplayer game with leaderboards, in-app purchases, and social features" \
  --analyze
```

Claude will analyze and create:
- Mobile app structure (React Native)
- Backend API (Node.js + Socket.io for real-time)
- Database (PostgreSQL + Redis)
- Payment integration (Stripe)
- Real-time communication agents
- Game state management agents

## 🔧 Configuration

### Config File

Create `~/.claude-gen/config.yaml`:

```yaml
# Default settings
defaults:
  model: claude-sonnet-4
  backend: python-fastapi
  frontend: react-typescript
  database: postgresql

# API keys
api:
  anthropic_key: ${ANTHROPIC_API_KEY}

# Output preferences
output:
  verbose: false
  json: false

# Template preferences
templates:
  custom_template_dir: ~/my-templates
```

### Environment Variables

```bash
# API key for Claude analysis
export ANTHROPIC_API_KEY="sk-ant-..."

# Default model
export CLAUDE_MODEL="claude-sonnet-4"

# Config file location
export CLAUDE_GEN_CONFIG="~/.claude-gen/config.yaml"
```

## 🐛 Troubleshooting

### "claude-gen: command not found"

**Solution:**
```bash
# Make sure you installed it
pip install claude-code-generator

# Or use Python module syntax
python -m src.cli.main init

# Check your PATH
echo $PATH

# Try reinstalling
pip uninstall claude-code-generator
pip install claude-code-generator
```

### "Output directory already exists"

**Solution:**
```bash
# Use --force to overwrite
claude-gen init --output ./existing-dir --force

# Or use --merge to combine
claude-gen init --output ./existing-dir --merge

# Or choose a different directory
claude-gen init --output ./new-dir
```

### "API key not found"

**Solution:**
```bash
# Set environment variable
export ANTHROPIC_API_KEY="sk-ant-..."

# Or pass directly
claude-gen init --api-key "sk-ant-..." --analyze

# Or add to config file
echo "api:\n  anthropic_key: sk-ant-..." >> ~/.claude-gen/config.yaml
```

### Using from Claude Code: "Agent not found"

**Solution:**
1. Make sure you're in the claude-code-generator directory or a generated project
2. Check that `.claude/agents/project-generator-agent.md` exists
3. Verify Claude Code can see the `.claude/` directory
4. Try reloading Claude Code

### Using from Claude Code: "claude-gen command not found"

**Solution:**

The project-generator-agent will fall back to running from source:

```bash
cd /path/to/claude-code-generator
python -m src.cli.main init --interactive
```

Or install globally:
```bash
pip install -e /path/to/claude-code-generator
```

## 📖 Next Steps

After generating a project:

1. **Review the Structure**
   ```bash
   cd your-project-name
   tree -L 3 -I '__pycache__|*.pyc'
   ```

2. **Read the Agents**
   ```bash
   ls .claude/agents/
   cat .claude/agents/api-development-agent.md
   ```

3. **Run Setup**
   - In Claude Code: `/setup-dev`
   - From terminal: `./scripts/setup-dev.sh`

4. **Start Building**
   - Ask Claude Code to build features
   - Agents will activate automatically based on your tasks

5. **Explore Commands**
   ```bash
   ls .claude/commands/
   ```

## 🤝 Contributing

Want to add your own templates or agents to the library?

```bash
# Add a new agent template
claude-gen add-template --type agent --file my-agent.md

# Add a new skill
claude-gen add-template --type skill --directory my-skill/

# Test your template
claude-gen test --template my-agent.md
```

See `CONTRIBUTING.md` for more details.

## 📄 License

MIT License - see LICENSE file for details.
