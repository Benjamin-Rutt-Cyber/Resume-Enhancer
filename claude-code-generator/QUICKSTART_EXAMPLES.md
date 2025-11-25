# Claude Code Generator - Quickstart Examples

Real-world examples you can run right now to generate complete Claude Code projects.

---

## Table of Contents

1. [SaaS Web Apps](#saas-web-apps)
2. [API Services](#api-services)
3. [Mobile Apps](#mobile-apps)
4. [IoT & Hardware](#iot--hardware)
5. [Data Science](#data-science)
6. [Common Scenarios](#common-scenarios)

---

## SaaS Web Apps

### Example 1: Task Management Platform

**Use Case:** Team collaboration and task tracking

```bash
claude-gen init \
  --project "TaskFlow" \
  --description "A task management platform with team collaboration, \
                 real-time updates, kanban boards, user authentication, \
                 and email notifications" \
  --type saas-web-app
```

**What You Get:**
- **Agents:** API Development, Frontend (React), Database, Testing, Deployment, Security
- **Skills:** Python FastAPI, React TypeScript, PostgreSQL, Authentication, REST API, Docker
- **Commands:** /setup-dev, /run-server, /run-tests, /deploy, /db-migrate
- **Docs:** ARCHITECTURE.md, API.md, TESTING.md

**Generated Structure:**
```
taskflow/
├── .claude/
│   ├── agents/       # 6 specialized agents
│   ├── skills/       # 6 framework skills
│   ├── commands/     # 5 slash commands
│   └── plugins.yaml  # React, Prettier, Black, ESLint
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── TESTING.md
└── README.md
```

---

### Example 2: E-Commerce Platform

**Use Case:** Online store with payments

```bash
claude-gen init \
  --project "ShopHub" \
  --description "E-commerce platform with product catalog, shopping cart, \
                 Stripe payment integration, user accounts, order management, \
                 and admin dashboard" \
  --type saas-web-app
```

**What You Get:**
- Same base structure as Task Management
- **Additional Features Detected:** payments, authentication
- **Plugin Recommendations:** Stripe integration, payment-related tools

**Key Files:**
- `.claude/skills/authentication/` - JWT auth, session management
- `.claude/agents/security-agent.md` - Payment security best practices
- `docs/API.md` - Payment endpoints documented

---

### Example 3: Social Media Platform

**Use Case:** User-generated content and real-time interactions

```bash
claude-gen init \
  --project "ConnectHub" \
  --description "Social media platform with user profiles, posts, comments, \
                 real-time chat using websockets, file uploads, and notifications" \
  --type saas-web-app
```

**What You Get:**
- **Features Detected:** websockets (real-time), authentication, file uploads
- **Skills Include:** WebSocket integration, file storage strategies
- **Architecture:** Includes real-time communication patterns

---

### Example 4: SaaS with Vue Frontend

**Use Case:** Dashboard application with Vue.js

```bash
claude-gen init \
  --project "AnalyticsDash" \
  --description "Analytics dashboard SaaS using Vue.js and TypeScript for frontend, \
                 FastAPI backend, PostgreSQL database, with data visualization" \
  --type saas-web-app
```

**What You Get:**
- **Frontend:** Vue TypeScript skill (instead of React)
- **Plugins:** Vue DevTools, Vetur recommended
- **Skills:** vue-typescript/, postgresql/, python-fastapi/

---

## API Services

### Example 5: User Management API

**Use Case:** Microservice for user authentication

```bash
claude-gen init \
  --project "UserAPI" \
  --description "RESTful API for user management with JWT authentication, \
                 password hashing, email verification, and role-based access control" \
  --type api-service
```

**What You Get:**
- **Agents:** API Development, Database, Testing, Deployment, Security, Documentation
- **Skills:** Python FastAPI, PostgreSQL, Authentication, REST API Design, Docker
- **Commands:** /setup-dev, /run-server, /run-tests, /deploy
- **No Frontend:** API-only structure

**Generated Structure:**
```
userapi/
├── .claude/
│   ├── agents/       # 6 agents (no frontend agent)
│   ├── skills/       # 5 backend skills
│   ├── commands/     # 4 commands
│   └── plugins.yaml  # Black, Pylint, pytest-runner
├── docs/
│   ├── API.md        # Detailed API docs with OpenAPI
│   └── TESTING.md
└── README.md
```

---

### Example 6: Payment Processing API

**Use Case:** Stripe payment webhook handler

```bash
claude-gen init \
  --project "PaymentProcessor" \
  --description "API service for processing Stripe webhooks, handling payment events, \
                 updating order status, and sending confirmation emails" \
  --type api-service
```

**What You Get:**
- **Features:** Payments, email, webhooks
- **Skills:** Webhook handling patterns, payment processing
- **Plugins:** Stripe-related tools

---

### Example 7: Node.js Express API

**Use Case:** JavaScript/TypeScript API

```bash
claude-gen init \
  --project "NotificationAPI" \
  --description "Notification API using Node.js Express and TypeScript \
                 for sending emails, SMS, and push notifications" \
  --type api-service
```

**What You Get:**
- **Backend:** Node Express skill (instead of FastAPI)
- **Skills:** node-express/, authentication/, rest-api-design/
- **Plugins:** ESLint, Prettier, Jest recommended

---

### Example 8: GraphQL API

**Use Case:** GraphQL API service

```bash
claude-gen init \
  --project "GraphQLAPI" \
  --description "GraphQL API service for content management with queries, \
                 mutations, subscriptions, and real-time updates" \
  --type api-service
```

**What You Get:**
- **Skills:** GraphQL-specific patterns in api-development-agent
- **Features:** Real-time subscriptions, schema design
- **Docs:** GraphQL schema documentation

---

## Mobile Apps

### Example 9: Fitness Tracker

**Use Case:** Cross-platform fitness app

```bash
claude-gen init \
  --project "FitTrack" \
  --description "Mobile fitness tracking app for iOS and Android using React Native \
                 with workout logging, progress charts, and user authentication" \
  --type mobile-app
```

**What You Get:**
- **Agents:** Mobile (React Native), API Development, Testing, Deployment
- **Skills:** React Native, Python FastAPI, PostgreSQL, Push Notifications
- **Commands:** /setup-dev, /run-ios, /run-android, /run-tests, /build-release
- **Docs:** Mobile app architecture, platform-specific guides

**Generated Structure:**
```
fittrack/
├── .claude/
│   ├── agents/       # Mobile-focused agents
│   ├── skills/       # React Native, mobile patterns
│   ├── commands/     # iOS/Android commands
│   └── plugins.yaml  # React Native tools
├── docs/
│   ├── ARCHITECTURE.md  # Mobile architecture
│   └── TESTING.md       # Mobile testing
└── README.md
```

---

### Example 10: Social Chat App

**Use Case:** Real-time messaging app

```bash
claude-gen init \
  --project "ChatApp" \
  --description "Mobile chat application with real-time messaging using websockets, \
                 push notifications, media sharing, and group chats" \
  --type mobile-app
```

**What You Get:**
- **Features:** Websockets, push notifications, file uploads
- **Skills:** Real-time communication, media handling
- **Architecture:** Real-time sync patterns

---

## IoT & Hardware

### Example 11: Temperature Monitor

**Use Case:** Raspberry Pi Pico temperature sensor

```bash
claude-gen init \
  --project "TempMonitor" \
  --description "IoT temperature monitoring system using Raspberry Pi Pico W \
                 with WiFi connectivity, MQTT for data transmission, \
                 and cloud logging" \
  --type hardware-iot
```

**What You Get:**
- **Agents:** Embedded IoT, Testing, Cloud Integration, Documentation
- **Skills:** MicroPython, MQTT, Sensor Integration, WiFi Communication
- **Commands:** /flash-firmware, /monitor-serial, /test-hardware, /deploy-ota
- **Docs:** HARDWARE.md, FIRMWARE.md

**Generated Structure:**
```
tempmonitor/
├── .claude/
│   ├── agents/       # IoT-focused agents
│   ├── skills/       # MicroPython, MQTT, sensors
│   ├── commands/     # Hardware commands
│   └── plugins.yaml  # MicroPython tools
├── docs/
│   ├── HARDWARE.md   # Hardware setup guide
│   ├── FIRMWARE.md   # Firmware documentation
│   └── TESTING.md
└── README.md
```

---

### Example 12: Smart Home Controller

**Use Case:** ESP32-based home automation

```bash
claude-gen init \
  --project "SmartHome" \
  --description "Smart home controller using ESP32 with WiFi, controlling lights, \
                 temperature, and security sensors via MQTT and REST API" \
  --type hardware-iot
```

**What You Get:**
- **Platform:** ESP32 (detected from description)
- **Skills:** MQTT, HTTP clients, sensor/actuator control
- **Features:** Multiple sensor types, cloud integration

---

### Example 13: Wearable Device

**Use Case:** Arduino-based fitness tracker

```bash
claude-gen init \
  --project "WearableTracker" \
  --description "Arduino wearable device for tracking steps, heart rate, \
                 and sleep using sensors with Bluetooth data sync" \
  --type hardware-iot
```

**What You Get:**
- **Platform:** Arduino (detected)
- **Connectivity:** Bluetooth (instead of WiFi)
- **Skills:** Sensor fusion, power management

---

## Data Science

### Example 14: Churn Prediction Model

**Use Case:** Customer churn prediction

```bash
claude-gen init \
  --project "ChurnPredictor" \
  --description "Machine learning model to predict customer churn using \
                 historical data, feature engineering, and scikit-learn" \
  --type data-science
```

**What You Get:**
- **Agents:** Data Science, Testing, Deployment, Documentation
- **Skills:** Python, Jupyter Notebooks, Data Visualization, Machine Learning
- **Commands:** /setup-dev, /run-notebook, /run-tests, /train-model
- **Docs:** Model documentation, data pipeline

**Generated Structure:**
```
churnpredictor/
├── .claude/
│   ├── agents/       # Data science agents
│   ├── skills/       # ML, data viz, notebooks
│   ├── commands/     # Notebook, training commands
│   └── plugins.yaml  # Jupyter, pandas tools
├── docs/
│   ├── DATA.md       # Data documentation
│   ├── MODEL.md      # Model documentation
│   └── TESTING.md
└── README.md
```

---

### Example 15: Sentiment Analysis

**Use Case:** NLP sentiment analysis

```bash
claude-gen init \
  --project "SentimentAnalyzer" \
  --description "NLP model for sentiment analysis of customer reviews using \
                 transformers, BERT, and PyTorch with API deployment" \
  --type data-science
```

**What You Get:**
- **Skills:** NLP-specific patterns, transformer models
- **Features:** Model serving API
- **Architecture:** Training + serving architecture

---

### Example 16: Recommendation Engine

**Use Case:** Product recommendation system

```bash
claude-gen init \
  --project "RecommendEngine" \
  --description "Recommendation system for e-commerce using collaborative filtering, \
                 matrix factorization, and real-time prediction API" \
  --type data-science
```

**What You Get:**
- **Skills:** Recommendation algorithms, real-time serving
- **Features:** Model training + API deployment
- **Docs:** Algorithm documentation, performance metrics

---

## Common Scenarios

### Scenario 1: Specify Exact Tech Stack

**Want Django instead of FastAPI?**

```bash
claude-gen init \
  --project "BlogPlatform" \
  --description "Blog platform using Django framework with admin panel, \
                 user authentication, and markdown support" \
  --type saas-web-app
```

**Result:** Selects Django skill instead of FastAPI

---

### Scenario 2: Multi-Feature Project

**Complex project with many features:**

```bash
claude-gen init \
  --project "SuperApp" \
  --description "All-in-one platform with user authentication, payment processing, \
                 real-time chat via websockets, file uploads to S3, email notifications, \
                 admin dashboard, and REST API" \
  --type saas-web-app
```

**Result:**
- All features detected: auth, payments, websockets, email, file uploads
- Comprehensive agent selection
- Detailed architecture docs

---

### Scenario 3: Minimal API

**Simple, focused API:**

```bash
claude-gen init \
  --project "HealthCheck" \
  --description "Simple health check API service with status endpoints" \
  --type api-service
```

**Result:**
- Minimal agent/skill selection
- Focused on core API development
- Quick setup

---

### Scenario 4: Microservices Architecture

**Multiple related services:**

```bash
# Service 1: User Service
claude-gen init \
  --project "UserService" \
  --description "Microservice for user management with JWT authentication" \
  --type api-service \
  --output ./microservices/user-service

# Service 2: Order Service
claude-gen init \
  --project "OrderService" \
  --description "Microservice for order processing and management" \
  --type api-service \
  --output ./microservices/order-service

# Service 3: Notification Service
claude-gen init \
  --project "NotificationService" \
  --description "Microservice for sending email and SMS notifications" \
  --type api-service \
  --output ./microservices/notification-service
```

**Result:** Three related microservices with consistent structure

---

### Scenario 5: Skip AI Analysis

**Use keyword detection (faster, no API key needed):**

```bash
claude-gen init \
  --project "QuickAPI" \
  --description "REST API for managing tasks with PostgreSQL database" \
  --type api-service \
  --no-ai
```

**Result:**
- Uses keyword-based detection
- Still generates complete project
- Faster generation

---

### Scenario 6: Custom Output Location

**Generate in specific directory:**

```bash
claude-gen init \
  --project "MyProject" \
  --description "A web application for team collaboration" \
  --output ~/projects/my-company/myproject
```

**Result:** Project generated at specified path

---

### Scenario 7: Overwrite Existing

**Regenerate an existing project:**

```bash
claude-gen init \
  --project "MyApp" \
  --description "Updated description with new features" \
  --overwrite
```

**Result:** Overwrites existing files (use with caution!)

---

### Scenario 8: Skip Plugins

**Don't want plugin recommendations:**

```bash
claude-gen init \
  --project "SimpleApp" \
  --description "Basic web app" \
  --no-plugins
```

**Result:** No `.claude/plugins.yaml` generated

---

## Quick Reference

### Command Cheat Sheet

```bash
# Interactive (easiest)
claude-gen init

# Full specification
claude-gen init --project "Name" --description "..." --type saas-web-app

# With options
claude-gen init \
  --project "Name" \
  --description "..." \
  --type saas-web-app \
  --output ./myproject \
  --no-ai \
  --no-plugins

# List available types
claude-gen list-types

# Validate generated project
claude-gen validate ./myproject
```

### Project Type Quick Picker

| You're Building | Use Type |
|-----------------|----------|
| Web app (frontend + backend) | `saas-web-app` |
| API only | `api-service` |
| iOS/Android app | `mobile-app` |
| Arduino/Pi/ESP32 | `hardware-iot` |
| ML model/data analysis | `data-science` |

### Description Keywords

Include these keywords for better detection:

**Authentication:** auth, login, JWT, OAuth, user accounts
**Payments:** payment, Stripe, subscription, checkout
**Real-time:** websocket, real-time, live updates, chat
**Email:** email, notifications, SMTP
**Files:** upload, S3, file storage, media

**Frameworks:**
- **Backend:** FastAPI, Django, Express, Gin, Rails
- **Frontend:** React, Vue, Angular, Svelte
- **Mobile:** React Native, Flutter
- **IoT:** MicroPython, Arduino, ESP32, Pico

**Databases:** PostgreSQL, MongoDB, MySQL, Redis

---

## Next Steps After Generation

### 1. Navigate to Project

```bash
cd your-project-name
```

### 2. Read the README

```bash
cat README.md
```

### 3. Review Architecture

```bash
cat docs/ARCHITECTURE.md
```

### 4. Explore Agents

```bash
ls -la .claude/agents/
cat .claude/agents/api-development-agent.md
```

### 5. Check Available Commands

```bash
ls -la .claude/commands/
```

### 6. Start Development with Claude Code

```bash
claude  # Launch Claude Code in the project
```

### 7. Use Slash Commands

In Claude Code:
```
/setup-dev     # Set up development environment
/run-server    # Start the server
/run-tests     # Run tests
```

---

## Tips for Better Results

### 1. Be Specific

**Good:**
```bash
--description "Task management SaaS with React frontend, FastAPI backend, \
               PostgreSQL database, user authentication, and email notifications"
```

**Avoid:**
```bash
--description "A web app"
```

### 2. Mention Tech Stack

Include framework names:
- "using Django" instead of "using Python"
- "with React TypeScript" instead of "with frontend"
- "PostgreSQL database" instead of "database"

### 3. List Key Features

- Authentication
- Payments
- Real-time features
- File uploads
- Integrations

### 4. Use Validation

Always validate after generation:

```bash
claude-gen validate ./your-project
```

---

## Troubleshooting Examples

### Problem: Wrong Project Type Detected

**Solution:** Force the type

```bash
# Let's say it detected api-service but you want saas-web-app
claude-gen init \
  --project "MyApp" \
  --description "..." \
  --type saas-web-app  # Force the type
```

---

### Problem: Missing Expected Agent

**Solution:** Make description more specific

```bash
# Add framework names explicitly
claude-gen init \
  --project "MyApp" \
  --description "Web app using React for frontend and FastAPI for backend"
```

---

### Problem: Too Many/Too Few Skills

**Result:** This is normal! The generator selects based on:
- Project type
- Tech stack mentioned
- Features described

You can always add/remove skills after generation.

---

## More Examples

For more examples and patterns, see:
- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Creating custom templates
- **[README.md](README.md)** - Project overview

---

## Get Help

- 📖 Read [USER_GUIDE.md](USER_GUIDE.md)
- 🐛 Report issues on [GitHub](https://github.com/yourusername/claude-code-generator/issues)
- 💬 Ask questions in [Discussions](https://github.com/yourusername/claude-code-generator/discussions)

---

**Ready to generate?** Pick an example above and try it now! 🚀
