# Claude Code Generator - User Guide

**Version:** 0.2.0
**Last Updated:** 2025-11-20

Welcome to the Claude Code Generator! This guide will help you create production-ready Claude Code project environments with optional starter code from simple descriptions.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Boilerplate Code Generation](#boilerplate-code-generation) ✨ NEW!
4. [Commands Reference](#commands-reference)
5. [Project Types](#project-types)
6. [Tech Stack Options](#tech-stack-options)
7. [Plugin Recommendations](#plugin-recommendations)
8. [Generated Project Structure](#generated-project-structure)
9. [Customization](#customization)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)
12. [FAQ](#faq)

---

## Installation

### Prerequisites

- **Python 3.9+** (3.14 recommended)
- **pip** package manager
- **Git** (for version control)
- **Claude Code CLI** (optional, for testing generated projects)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-code-generator.git
cd claude-code-generator

# Install in development mode
pip install -e .

# Verify installation
claude-gen --version
```

### Optional: Configure API Key

For AI-powered project analysis (recommended):

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Or add to your shell profile (~/.bashrc, ~/.zshrc)
echo 'export ANTHROPIC_API_KEY="your-api-key"' >> ~/.bashrc
```

**Without API key:** The generator will use keyword-based detection (still works great!)

---

## Quick Start

### Generate Your First Project

```bash
# Interactive mode (easiest)
claude-gen init

# You'll be prompted for:
# - Project name: "My Task Manager"
# - Description: "A task management app with user auth and real-time updates"

# Press Enter to confirm and generate!
```

### Generate with Options

```bash
claude-gen init \
  --project "TaskFlow" \
  --description "A project management SaaS with team collaboration, \
                 real-time updates, and integrations" \
  --type saas-web-app
```

### Generate with Starter Code ✨ NEW!

```bash
# Generate with production-ready boilerplate code
claude-gen init \
  --project "FastAPI Backend" \
  --description "REST API with FastAPI, PostgreSQL, and authentication" \
  --with-code

# Generates:
# - Complete FastAPI application structure
# - Configuration files (docker-compose, .env, requirements.txt)
# - Ready-to-run backend code
# - Docker setup for development
```

### What Gets Generated

```
taskflow/
├── .claude/
│   ├── agents/          # 6 specialized agents
│   ├── skills/          # 5-7 framework skills
│   ├── commands/        # 5-8 slash commands
│   └── plugins.yaml     # Plugin recommendations
├── docs/
│   ├── ARCHITECTURE.md  # Architecture guide
│   ├── API.md           # API documentation
│   └── TESTING.md       # Testing strategy
├── README.md            # Project overview
└── .gitignore           # Comprehensive gitignore
```

---

## Boilerplate Code Generation

Generate production-ready starter code along with your Claude Code environment using the `--with-code` flag.

### What is Boilerplate Generation?

Instead of just creating the `.claude/` configuration directory, the generator can also create:
- **Complete application structure** with working code
- **Configuration files** (Docker, .env, docker-compose.yml)
- **Dependency files** (requirements.txt, package.json)
- **Ready-to-run code** that you can immediately test and build upon

### Supported Frameworks

#### Backend Frameworks
- **FastAPI** (Python)
  - Complete FastAPI application with:
    - Main application file with CORS middleware
    - App structure (`app/core/`, `app/api/routes/`)
    - Health check endpoint
    - Configuration management
    - Dockerfile and docker-compose setup

#### Frontend Frameworks
- **Next.js 14+**
  - App Router structure
  - TypeScript configuration
  - Components and layouts
  - API routes
  - Tailwind CSS setup

- **React (Vite)**
  - Vite + React + TypeScript
  - Component structure
  - Routing setup
  - Build configuration

### How to Use

```bash
# Backend only (FastAPI)
claude-gen init \
  --project "My API" \
  --description "REST API with FastAPI and PostgreSQL" \
  --with-code

# Frontend only (Next.js)
claude-gen init \
  --project "My App" \
  --description "Next.js application with TypeScript" \
  --with-code

# Full-stack (FastAPI + React)
claude-gen init \
  --project "Full Stack App" \
  --description "FastAPI backend with React frontend" \
  --with-code
```

### What Gets Generated

**Backend (FastAPI):**
```
my-api/
├── main.py                 # FastAPI application entry point
├── app/
│   ├── core/
│   │   └── config.py      # Configuration management
│   ├── api/
│   │   └── routes/
│   │       └── health.py  # Health check endpoint
│   └── __init__.py
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-service setup
├── .env.example           # Environment template
├── .gitignore            # Comprehensive gitignore
└── .claude/              # Claude Code configuration
```

**Frontend (Next.js):**
```
my-app/
├── src/
│   ├── app/
│   │   ├── layout.tsx     # Root layout
│   │   ├── page.tsx       # Home page
│   │   └── api/
│   │       └── health/    # API routes
│   ├── components/
│   │   └── Header.tsx     # Example component
│   └── lib/
│       └── utils.ts       # Utilities
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── next.config.js         # Next.js config
└── .claude/              # Claude Code configuration
```

### Getting Started with Generated Code

After generation with `--with-code`:

1. **Install dependencies:**
   ```bash
   # Python backend
   pip install -r requirements.txt

   # Node.js frontend
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the application:**
   ```bash
   # FastAPI backend
   uvicorn main:app --reload

   # Next.js frontend
   npm run dev
   ```

4. **Or use Docker:**
   ```bash
   docker-compose up
   ```

---

## Commands Reference

### `claude-gen init`

Generate a new Claude Code project.

**Usage:**
```bash
claude-gen init [OPTIONS]
```

**Options:**

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--project` | `-p` | Project name | `--project "My App"` |
| `--description` | `-d` | Project description | `--description "A task manager"` |
| `--type` | `-t` | Project type | `--type saas-web-app` |
| `--output` | `-o` | Output directory | `--output ./my-app` |
| `--with-code` | | Generate starter code/boilerplate ✨ NEW! | `--with-code` |
| `--overwrite` | | Overwrite existing files | `--overwrite` |
| `--no-ai` | | Skip AI analysis | `--no-ai` |
| `--no-plugins` | | Skip plugin recommendations | `--no-plugins` |
| `--no-ai-plugins` | | Skip AI plugin analysis | `--no-ai-plugins` |

**Examples:**

```bash
# Interactive mode
claude-gen init

# Specify everything
claude-gen init \
  --project "ECommerce" \
  --description "Online store with payments" \
  --type saas-web-app \
  --output ~/projects/ecommerce

# Use keyword detection (no AI)
claude-gen init \
  --project "IoT Sensor" \
  --description "Temperature monitor using Pico W" \
  --no-ai

# Skip plugin recommendations
claude-gen init \
  --project "Simple API" \
  --description "REST API for users" \
  --no-plugins
```

---

### `claude-gen list-types`

List all available project types with descriptions.

**Usage:**
```bash
claude-gen list-types [OPTIONS]
```

**Options:**

| Option | Description | Example |
|--------|-------------|---------|
| `--templates-dir` | Custom templates directory | `--templates-dir ./custom-templates` |

**Example:**
```bash
claude-gen list-types
```

**Output:**
```
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Type         ┃ Display Name   ┃ Description                     ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ saas-web-app │ SaaS Web App   │ Full-stack web application      │
│ api-service  │ API Service    │ RESTful API backend             │
│ mobile-app   │ Mobile App     │ iOS/Android application         │
│ hardware-iot │ Hardware IoT   │ IoT device firmware             │
│ data-science │ Data Science   │ ML/AI and data analysis         │
└──────────────┴────────────────┴─────────────────────────────────┘
```

---

### `claude-gen validate`

Validate a generated project structure.

**Usage:**
```bash
claude-gen validate PATH
```

**Example:**
```bash
claude-gen validate ./my-project
```

**Output:**
```
Validating project at: ./my-project

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Check            ┃ Status ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ .claude directory│ [PASS] │
│ .claude/agents   │ [PASS] │
│ .claude/skills   │ [PASS] │
│ .claude/commands │ [PASS] │
│ README.md        │ [PASS] │
│ docs directory   │ [PASS] │
└──────────────────┴────────┘

✓ All checks passed!
```

---

## Project Types

### 1. SaaS Web App (`saas-web-app`)

**Best for:** Full-stack web applications with frontend + backend

**Generated Components:**
- **Agents:** API Development, Frontend, Database, Testing, Deployment, Security
- **Skills:** Python FastAPI, React TypeScript, PostgreSQL, Authentication, REST API Design, Docker
- **Commands:** /setup-dev, /run-server, /run-tests, /deploy, /db-migrate

**Example Projects:**
- Project management platforms
- Team collaboration tools
- E-commerce platforms
- Social media applications
- CRM systems

**Example:**
```bash
claude-gen init \
  --project "TeamHub" \
  --description "A team collaboration platform with chat, \
                 file sharing, and project management" \
  --type saas-web-app
```

---

### 2. API Service (`api-service`)

**Best for:** Backend-only REST APIs and microservices

**Generated Components:**
- **Agents:** API Development, Database, Testing, Deployment, Security, Documentation
- **Skills:** Python FastAPI, PostgreSQL, REST API Design, Authentication, Docker
- **Commands:** /setup-dev, /run-server, /run-tests, /deploy

**Example Projects:**
- Microservices
- Third-party integrations
- Data processing APIs
- Authentication services
- Payment gateways

**Example:**
```bash
claude-gen init \
  --project "UserAPI" \
  --description "RESTful API for user management with JWT auth" \
  --type api-service
```

---

### 3. Mobile App (`mobile-app`)

**Best for:** iOS and Android applications

**Generated Components:**
- **Agents:** Mobile React Native, API Development, Testing, Deployment
- **Skills:** React Native, Python FastAPI, PostgreSQL, Mobile Push Notifications
- **Commands:** /setup-dev, /run-ios, /run-android, /run-tests, /build-release

**Example Projects:**
- Social apps
- Productivity tools
- E-commerce mobile apps
- Fitness trackers
- News readers

**Example:**
```bash
claude-gen init \
  --project "FitTracker" \
  --description "Mobile fitness tracking app with workout logging" \
  --type mobile-app
```

---

### 4. Hardware IoT (`hardware-iot`)

**Best for:** IoT devices, embedded systems, hardware projects

**Generated Components:**
- **Agents:** Embedded IoT, Testing, Cloud Integration, Documentation
- **Skills:** MicroPython, MQTT, Sensor Integration, WiFi Communication
- **Commands:** /flash-firmware, /monitor-serial, /test-hardware, /deploy-ota

**Example Projects:**
- Temperature sensors
- Smart home devices
- Environmental monitors
- Wearable devices
- Industrial IoT

**Example:**
```bash
claude-gen init \
  --project "TempMonitor" \
  --description "Temperature monitoring system using Raspberry Pi Pico W \
                 with MQTT and cloud logging" \
  --type hardware-iot
```

---

### 5. Data Science (`data-science`)

**Best for:** Machine learning, data analysis, and AI projects

**Generated Components:**
- **Agents:** Data Science, Testing, Deployment, Documentation
- **Skills:** Python, Jupyter Notebooks, Data Visualization, Machine Learning
- **Commands:** /setup-dev, /run-notebook, /run-tests, /train-model

**Example Projects:**
- Prediction models
- Data analysis pipelines
- Recommendation systems
- Image classification
- Natural language processing

**Example:**
```bash
claude-gen init \
  --project "ChurnPredictor" \
  --description "Machine learning model to predict customer churn" \
  --type data-science
```

---

## Tech Stack Options

### Backend Frameworks

The generator detects or selects backend frameworks based on your description:

| Framework | Keywords | Best For |
|-----------|----------|----------|
| **python-fastapi** | fastapi, python, api | Modern async APIs |
| **node-express** | node, express, javascript | JavaScript ecosystem |
| **django** | django, python | Full-featured web apps |
| **go-gin** | go, golang, gin | High-performance APIs |

**Example:**
```bash
# Will select Django
claude-gen init \
  --project "Blog" \
  --description "A blog platform using Django with admin panel"
```

### Frontend Frameworks

| Framework | Keywords | Best For |
|-----------|----------|----------|
| **nextjs** ✨ NEW! | next, nextjs, next.js | Full-stack React with SSR, App Router |
| **nuxt** ✨ NEW! | nuxt, nuxtjs, nuxt3 | Full-stack Vue with SSR, auto-imports |
| **svelte** ✨ NEW! | svelte, sveltekit | Reactive UI with SvelteKit |
| **angular** ✨ NEW! | angular, ng | Enterprise TypeScript framework |
| **react-typescript** | react, typescript | Modern SPAs |
| **vue-typescript** | vue, vuejs, typescript | Progressive apps |
| **react-native** | mobile, ios, android | Mobile apps |

**New Modern Framework Features:**
- **Next.js 14+**: App Router, Server Components, Server Actions, streaming SSR
- **Nuxt 3**: Composition API, auto-imports, file-based routing, server routes
- **SvelteKit**: Reactive declarations, stores, file-based routing, adapters
- **Angular**: Components, services, dependency injection, RxJS, routing

### Databases

| Database | Keywords | Best For |
|----------|----------|----------|
| **postgresql** | postgres, postgresql, sql | Relational data |
| **mongodb** | mongo, mongodb, nosql | Document storage |
| **mysql** | mysql, mariadb | Traditional SQL |

### IoT Platforms

| Platform | Keywords | Best For |
|----------|----------|----------|
| **pico-w** | pico, pico w, raspberry pi pico | WiFi-enabled projects |
| **esp32** | esp32, espressif | Dual-core microcontroller |
| **arduino** | arduino, uno, mega | Beginner-friendly |

---

## Plugin Recommendations

### How It Works

The generator automatically recommends Claude Code marketplace plugins based on:
1. **Project Type** - Essential tools for your project category
2. **Tech Stack** - Language/framework-specific tools
3. **Features** - Authentication, payments, etc.
4. **AI Analysis** - Context-aware suggestions (with API key)

### Recommendation Priorities

**High Priority** - Essential for your project:
- Code formatters (Black, Prettier)
- Linters (ESLint, Pylint)
- Framework tools (React DevTools)

**Medium Priority** - Helpful productivity tools:
- GitHub integration
- Testing runners
- Deployment helpers

**Low Priority** - Nice-to-have enhancements:
- Git assistants
- Documentation generators

### Example Output

```yaml
# .claude/plugins.yaml
recommended_plugins:
  high_priority:
    - name: black
      reason: Python code formatting (PEP 8 compliance)
      install_command: /plugin install black
      category: code-quality

    - name: prettier
      reason: JavaScript/TypeScript/React formatting
      install_command: /plugin install prettier
      category: code-quality

  medium_priority:
    - name: github-actions
      reason: CI/CD workflow management
      install_command: /plugin install github-actions
      category: devops
```

### Installing Plugins

```bash
# Navigate to your project
cd my-project

# View recommendations
cat .claude/plugins.yaml

# Install a plugin
/plugin install black

# Install multiple
/plugin install black prettier pytest-runner
```

### Skipping Plugin Recommendations

```bash
# Skip all plugin recommendations
claude-gen init --no-plugins --project "..." --description "..."

# Skip AI analysis, keep project-type recommendations
claude-gen init --no-ai-plugins --project "..." --description "..."
```

---

## Generated Project Structure

### Typical SaaS Web App Structure

```
my-saas-app/
├── .claude/
│   ├── agents/
│   │   ├── api-development-agent.md      # API development expert
│   │   ├── frontend-react-agent.md       # React/UI expert
│   │   ├── database-postgres-agent.md    # Database expert
│   │   ├── testing-agent.md              # Testing specialist
│   │   ├── deployment-agent.md           # DevOps expert
│   │   └── security-agent.md             # Security specialist
│   │
│   ├── skills/
│   │   ├── python-fastapi/
│   │   │   ├── SKILL.md                  # FastAPI framework
│   │   │   └── examples/
│   │   ├── react-typescript/
│   │   │   ├── SKILL.md                  # React + TypeScript
│   │   │   └── examples/
│   │   ├── postgresql/
│   │   │   └── SKILL.md                  # PostgreSQL database
│   │   ├── authentication/
│   │   │   └── SKILL.md                  # Auth strategies
│   │   ├── rest-api-design/
│   │   │   └── SKILL.md                  # API design patterns
│   │   └── docker-deployment/
│   │       └── SKILL.md                  # Container deployment
│   │
│   ├── commands/
│   │   ├── setup-dev.md                  # /setup-dev
│   │   ├── run-server.md                 # /run-server
│   │   ├── run-tests.md                  # /run-tests
│   │   ├── deploy.md                     # /deploy
│   │   └── db-migrate.md                 # /db-migrate
│   │
│   └── plugins.yaml                      # Plugin recommendations
│
├── docs/
│   ├── ARCHITECTURE.md                   # System architecture
│   ├── API.md                            # API documentation
│   └── TESTING.md                        # Testing strategy
│
├── README.md                             # Project overview
└── .gitignore                            # Git ignore rules
```

### Typical IoT Project Structure

```
temp-monitor/
├── .claude/
│   ├── agents/
│   │   ├── embedded-iot-agent.md         # IoT development expert
│   │   ├── testing-agent.md              # Testing specialist
│   │   └── documentation-agent.md        # Documentation expert
│   │
│   ├── skills/
│   │   ├── micropython/
│   │   ├── mqtt/
│   │   └── sensor-integration/
│   │
│   ├── commands/
│   │   ├── flash-firmware.md             # /flash-firmware
│   │   ├── monitor-serial.md             # /monitor-serial
│   │   └── deploy-ota.md                 # /deploy-ota
│   │
│   └── plugins.yaml
│
├── docs/
│   ├── HARDWARE.md                       # Hardware setup
│   └── FIRMWARE.md                       # Firmware guide
│
└── README.md
```

---

## Customization

### Overriding Project Type Detection

If AI/keyword detection picks the wrong type:

```bash
# Force a specific type
claude-gen init \
  --project "MyApp" \
  --description "..." \
  --type api-service  # Override detection
```

### Custom Output Directory

```bash
# Generate in specific location
claude-gen init \
  --project "MyApp" \
  --description "..." \
  --output ~/projects/myapp

# Use absolute path
claude-gen init --output /home/user/dev/myapp ...
```

### Modifying Generated Files

After generation, you can:

1. **Edit Agents** - Customize agent instructions in `.claude/agents/`
2. **Add Skills** - Create new skills in `.claude/skills/`
3. **Create Commands** - Add custom slash commands in `.claude/commands/`
4. **Update Docs** - Modify documentation in `docs/`

---

## Troubleshooting

### Issue: "Command not found: claude-gen"

**Solution:**
```bash
# Ensure package is installed
pip install -e .

# Check if it's in PATH
which claude-gen

# Try running with python -m
python -m src.cli.main init
```

---

### Issue: "ANTHROPIC_API_KEY not found" Warning

**Not a Problem!** The generator will use keyword-based detection.

**To Enable AI Analysis:**
```bash
export ANTHROPIC_API_KEY="your-key"
```

---

### Issue: "Project directory already exists"

**Solution:**
```bash
# Use --overwrite to replace
claude-gen init --overwrite --project "..." --description "..."

# Or choose a different output directory
claude-gen init --output ./myapp-v2 --project "..." --description "..."
```

---

### Issue: "Description must be at least 10 characters"

**Solution:**
Provide a more detailed project description:

```bash
# Too short
claude-gen init --description "An app"

# Good
claude-gen init --description "A task management application with user authentication"
```

---

### Issue: Generated project missing expected agents/skills

**Possible Causes:**
1. Description wasn't detailed enough
2. Project type detection was incorrect

**Solution:**
```bash
# Provide more detail
claude-gen init \
  --project "MyApp" \
  --description "A SaaS platform with React frontend, FastAPI backend, \
                 PostgreSQL database, user authentication, and real-time chat"

# Or force the type
claude-gen init \
  --type saas-web-app \
  --project "..." \
  --description "..."
```

---

## Best Practices

### 1. Write Detailed Descriptions

**Good:**
```bash
claude-gen init \
  --description "A project management SaaS with team collaboration, \
                 real-time updates, task tracking, file uploads, \
                 user authentication, and email notifications"
```

**Avoid:**
```bash
claude-gen init --description "A web app"
```

### 2. Specify Key Technologies

Include framework/library names in your description:

```bash
claude-gen init \
  --description "A REST API using FastAPI and PostgreSQL for managing \
                 customer data with JWT authentication"
```

### 3. Mention Important Features

Feature keywords help select appropriate agents and skills:
- `authentication` / `login` / `auth`
- `payments` / `subscription` / `stripe`
- `email` / `notifications`
- `real-time` / `websockets`
- `file upload` / `storage`

### 4. Use Validation

Always validate generated projects:

```bash
claude-gen validate ./my-project
```

### 5. Review Generated Files

Before starting development:
1. Read `README.md` for project overview
2. Review `docs/ARCHITECTURE.md` for system design
3. Check `.claude/agents/` for available specialists
4. Explore `.claude/skills/` for framework guidance

### 6. Customize After Generation

The generated structure is a starting point:
- Modify agent instructions to fit your workflow
- Add custom skills for specialized libraries
- Create project-specific slash commands
- Expand documentation

---

## FAQ

### Q: Do I need an Anthropic API key?

**A:** No! The generator works without an API key using keyword-based detection. However, with an API key, you get:
- More accurate project type detection
- Better tech stack selection
- Smarter plugin recommendations

---

### Q: Can I use this for non-Python projects?

**A:** Yes! The generator supports multiple tech stacks:
- **Backend:** Python (FastAPI, Django), Node.js (Express), Go (Gin)
- **Frontend:** React, Vue, React Native
- **IoT:** MicroPython, CircuitPython
- **Data Science:** Python, Jupyter

Just mention your preferred stack in the description.

---

### Q: What if my project doesn't fit the 5 types?

**A:** The 5 types are broad categories:
- Web app = `saas-web-app`
- API-only = `api-service`
- Mobile = `mobile-app`
- Hardware = `hardware-iot`
- ML/Data = `data-science`

Most projects fit one of these. If not, choose the closest and customize after generation.

---

### Q: Can I generate multiple projects?

**A:** Yes! Generate as many as you want:

```bash
claude-gen init --output ./project1 --description "..."
claude-gen init --output ./project2 --description "..."
claude-gen init --output ./project3 --description "..."
```

---

### Q: How do I update a generated project?

**A:** Currently, you can't re-generate into an existing project. Best approach:
1. Generate a new project
2. Copy desired agents/skills/commands to existing project
3. Merge changes manually

---

### Q: Are the generated agents reusable?

**A:** Yes! The agents in `.claude/agents/` are:
- **Framework-agnostic** - Work with any tech stack
- **Comprehensive** - Cover all aspects of development
- **Copy-ready** - Can be copied between projects

---

### Q: What version of Claude Code is required?

**A:** The generated projects work with any recent version of Claude Code. The `.claude/` directory structure is standard.

---

### Q: Can I contribute new templates?

**A:** Yes! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Adding new agents
- Creating skills
- Designing commands
- Submitting project types

---

### Q: How do I report bugs or request features?

**A:** Open an issue on GitHub:
- **Bug Report:** Describe what went wrong, include command used
- **Feature Request:** Explain what you'd like to see
- **Question:** Ask anything!

---

## Next Steps

### Using Your Generated Project

1. **Navigate to project:**
   ```bash
   cd my-project
   ```

2. **Read the README:**
   ```bash
   cat README.md
   ```

3. **Set up development:**
   ```bash
   /setup-dev  # In Claude Code
   ```

4. **Start coding with Claude!**
   ```bash
   claude  # Launch Claude Code
   ```

### Learning More

- **[QUICKSTART_EXAMPLES.md](QUICKSTART_EXAMPLES.md)** - Common examples
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribute to the generator
- **[TESTING.md](TESTING.md)** - Test suite documentation
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Generator architecture

---

## Support

Need help?

- 📖 **Documentation:** Read this guide thoroughly
- 🐛 **Issues:** [GitHub Issues](https://github.com/yourusername/claude-code-generator/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/yourusername/claude-code-generator/discussions)
- 📧 **Email:** support@example.com

---

**Happy Generating!** 🚀

Transform your ideas into fully-configured Claude Code environments in seconds.
