# VBoarder - Multi-Agent Executive AI System

[![Version](https://img.shields.io/badge/version-0.9.0--beta.1-blue.svg)](./VERSION)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/next.js-14.2-black.svg)](https://nextjs.org/)
[![Tests](https://img.shields.io/badge/tests-25%2F25-brightgreen.svg)](./tests_flat/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

> **VBoarder** is an AI-powered multi-agent system featuring specialized executive agents (CEO, CTO, CFO, COO, CMO, CLO, COS, SEC, AIR) with persistent memory and RAG capabilities.

---

## 🚀 NEW: Command Console-Grade VS Code Workspace

**VBoarder now includes a production-ready VS Code workspace with one-click launchers!**

### Quick Setup (3 Commands)

```bash
# 1. Open workspace
code d:\ai\projects\vboarder

# 2. Install extensions (click "Install All" when prompted)

# 3. Launch full stack
Ctrl+Shift+P → "Tasks: Run Task" → "🔄 Full Stack Startup"
```

### What You Get

- ✅ **13 Task Runners** - Full Stack, Agent Repair, Tests, Cleanup
- ✅ **7 Debug Configurations** - Breakpoint debugging for backend, agents, tests
- ✅ **20+ Curated Extensions** - Python, GitLens, Copilot, Markdown, etc.
- ✅ **Auto-Everything** - Format on save, organize imports, activate Python env
- ✅ **Complete Documentation** - Quick ref, setup guide, troubleshooting

**See:** [`.vscode/QUICK_REFERENCE.md`](.vscode/QUICK_REFERENCE.md) or [`docs/VSCODE_SETUP_GUIDE.md`](docs/VSCODE_SETUP_GUIDE.md)

---

## 🎯 Quick Start (5 Minutes)

### Prerequisites

- **Python 3.12+** (with pip)
- **Node.js 20+** (with npm)
- **Ollama** running locally (or OpenAI API key)

### 1️⃣ Backend Setup

```bash
# Clone and navigate
git clone <repo-url>
cd vboarder

# Create environment configuration
cp .env.example .env
# Edit .env with your settings (API keys, model URLs)

# Install dependencies
pip install -r requirements.txt

# Run tests (verify setup)
pytest -v

# Start backend server
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

**Backend ready at:** http://127.0.0.1:3738
**API Docs:** http://127.0.0.1:3738/docs

### 2️⃣ Frontend Setup

```bash
# Navigate to frontend
cd vboarder_frontend/nextjs_space

# Create environment configuration
cp .env.example .env.local
# Verify NEXT_PUBLIC_API_BASE=http://127.0.0.1:3738

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend ready at:** http://localhost:3010

### 3️⃣ Verify Everything Works

```powershell
# Health check
curl http://127.0.0.1:3738/health

# Readiness check
curl http://127.0.0.1:3738/ready

# List agents
curl http://127.0.0.1:3738/agents

# Quick chat test
curl -X POST http://127.0.0.1:3738/chat/CEO `
  -H "Content-Type: application/json" `
  -d '{"message":"Hello!","session_id":"test","concise":true}'
```

**✅ If all commands succeed, you're ready to go!**

---

## 🎛️ Dev Dashboard (Easiest Way!)

**NEW:** One-click web dashboard to start/stop everything!

```bash
# Install Flask (one time)
pip install flask

# Start the dashboard
python devdash.py

# Open in browser
# http://127.0.0.1:4545
```

**Features:**

- ✅ Start/stop backend with one click
- ✅ Start/stop frontend with one click
- ✅ View live logs in browser
- ✅ Quick links to all endpoints
- ✅ No terminal juggling needed!

**Environment Variables (optional):**

```bash
export VB_BACKEND_PORT=3738    # Backend port (default: 3738)
export VB_FRONTEND_PORT=3010   # Frontend port (default: 3010)
export VB_DASH_PORT=4545       # Dashboard port (default: 4545)
```

---

## 🚀 Using Make (Developers)

```bash
# View all available commands
make help

# Start development server
make dev

# Run tests
make test

# Format code
make format

# Clean cache files
make clean

# Quick endpoint checks
make health
make ready
make agents
```

---

## 🧪 Testing

```bash
# Run all 25 tests
pytest -v

# Expected output:
# ✅ 25 passed (100%)
# - Health checks
# - Agent endpoints
# - Memory persistence
# - Chat functionality
# - Streaming support
```

## 💬 Chat with Agents

```bash
# CEO - Strategic leadership
curl -X POST http://localhost:3738/chat/CEO \
  -H "Content-Type: application/json" \
  -d '{"message":"What is our Q4 strategy?","session_id":"user123"}'

# CTO - Technology decisions
curl -X POST http://localhost:3738/chat/CTO \
  -H "Content-Type: application/json" \
  -d '{"message":"What tech stack should we use?","session_id":"user123"}'

# CFO - Financial planning
curl -X POST http://localhost:3738/chat/CFO \
  -H "Content-Type: application/json" \
  -d '{"message":"Review our budget allocation","session_id":"user123"}'
```

## 📝 Memory Operations

```bash
# Add a fact to CEO's memory
curl -X POST http://localhost:3738/api/memory \
  -H "Content-Type: application/json" \
  -d '{
    "agent":"CEO",
    "section":"facts",
    "entry":"Q3 revenue exceeded targets by 15%"
  }'

# Retrieve CEO's current memory
curl "http://localhost:3738/api/memory?agent=CEO"

# Get CEO's full context (for prompts)
curl "http://localhost:3738/api/context?agent=CEO&max_facts=10&max_messages=10"

# Add conversation message
curl -X POST http://localhost:3738/api/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "agent":"CEO",
    "message":"Board meeting scheduled for next week",
    "sender":"user",
    "session_id":"user123"
  }'
```

## 🎯 Agent Roles

| Agent   | Specialty         | Use When                                      |
| ------- | ----------------- | --------------------------------------------- |
| **CEO** | Strategy & Vision | Big picture decisions, company direction      |
| **CFO** | Finance           | Budgets, costs, revenue, financial analysis   |
| **COO** | Operations        | Processes, efficiency, day-to-day execution   |
| **CTO** | Technology        | Tech stack, architecture, engineering         |
| **CLO** | Legal             | Contracts, compliance, legal risks            |
| **CMO** | Marketing         | Branding, campaigns, customer acquisition     |
| **SEC** | Admin             | Scheduling, coordination, information routing |
| **AIR** | AI Research       | AI/ML evaluation, prototyping, research       |
| **COS** | Coordination      | Multi-agent orchestration, cross-functional   |

## 🔧 Common Tasks

### View Agent's Memory File

```bash
# Check what CEO knows
cat agents/CEO/memory.json | jq

# View full audit log
cat agents/CEO/memory.jsonl
```

### Reset Agent's Memory

```bash
# Clear specific section
curl -X DELETE "http://localhost:3738/api/memory?agent=CEO&section=facts"

# Or manually delete
rm agents/CEO/memory.json
rm agents/CEO/conversation_history.json
```

### Run Cleanup

```bash
# Compress and archive old logs/memory
python3 scripts/cleanup_logs_memory.py

# Or schedule via cron
0 2 * * * /path/to/vboarder/scripts/run_cleanup.sh
```

## 📊 Check System Status

```bash
# Health check
curl http://localhost:3738/health

# View all conversation sessions
ls -la data/conversations/

# Check disk usage
du -sh agents/*/memory.*
du -sh data/conversations/
du -sh logs/
```

## 🐛 Troubleshooting

### Tests Failing?

```bash
# Check if project is installed
pip install -e .

# Verify imports work
python -c "from api.main import app; print('✓ Imports OK')"
```

### Agent Not Remembering?

```bash
# Check if memory file exists
ls -la agents/CEO/memory.json

# Check file permissions
chmod 644 agents/CEO/memory.json

# Verify memory endpoint works
curl "http://localhost:3738/api/memory?agent=CEO"
```

### Port Already in Use?

```bash
# Find process on port 3738
lsof -i :3738

# Kill it
kill -9 <PID>

# Or use different port
uvicorn api.main:app --port 3739
```

## 📚 Documentation

- **Memory System:** `docs/MEMORY_SYSTEM_REPORT.md`
- **Agent Integration:** `docs/AGENT_MEMORY_INTEGRATION.md`
- **Function Reference:** `docs/AGENT_FUNCTIONS_REFERENCE.md`
- **Architecture Diagrams:** `docs/AGENT_ARCHITECTURE_DIAGRAM.md`
- **Deployment Guide:** `docs/DEPLOYMENT_STATUS.md`
- **API Docs:** http://localhost:3738/docs (auto-generated)

## 🎓 Code Examples

### Use Agent Logic Directly

```python
from agents.CEO.agent_logic import build_ceo_prompt

# Build memory-enriched prompt
prompt = await build_ceo_prompt("What's our priority?")
print(prompt)

# Output includes:
# - CEO persona
# - Recent facts
# - Conversation history
# - Role-specific instructions
```

### COS Orchestration

```python
from agents.COS.agent_logic import build_cos_prompt

# COS loads context from all peers
prompt = await build_cos_prompt("Coordinate product launch")

# Includes summaries from:
# CEO, CFO, COO, CTO, CLO, CMO, SEC, AIR
```

### Load Agent Context

```python
from api.memory_manager import load_agent_context

context = await load_agent_context(
    agent="CTO",
    max_facts=10,
    max_messages=10
)

# Returns:
# {
#   "agent": "CTO",
#   "persona": {...},
#   "facts": [...],
#   "recent_messages": [...],
#   "conversation_history": [...]
# }
```

---

## 🔧 Development Workflow

### Pre-commit Hooks (Recommended)

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

**Configured hooks:**

- Black (Python formatting)
- Ruff (Python linting)
- Prettier (JS/TS/JSON/YAML formatting)
- Trailing whitespace removal
- YAML/JSON validation

### Code Formatting

```bash
# Backend (Python)
make format
# OR manually:
black api tests_flat agents
ruff check api tests_flat --fix

# Frontend (TypeScript)
cd vboarder_frontend/nextjs_space
npm run format
```

### Dependency Management

```bash
# Lock backend dependencies
make freeze
# Creates requirements.lock

# Update frontend dependencies
cd vboarder_frontend/nextjs_space
npm audit fix
npm ci  # Install from lockfile
```

---

## 🚢 Deployment

### Production Build

```bash
# Backend - no special build needed
pip install -r requirements.txt

# Frontend - build static assets
cd vboarder_frontend/nextjs_space
npm ci
npm run build
npm run start  # Production server
```

### Health Checks for Load Balancers

```bash
# Basic health (always returns 200)
GET /health

# Comprehensive readiness check
# Returns 200 only if all systems operational
GET /ready
```

**K8s Liveness Probe:**

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 3738
  initialDelaySeconds: 10
  periodSeconds: 30
```

**K8s Readiness Probe:**

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 3738
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Environment Variables

**Backend (.env):**

```bash
API_KEY=your-production-key
LLM_MODE=openai  # or 'local' for Ollama
OPENAI_API_KEY=sk-...
STREAMING_ENABLED=true
ALLOWED_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
```

**Frontend (.env.local):**

```bash
NEXT_PUBLIC_API_BASE=https://api.yourdomain.com
NEXT_PUBLIC_API_KEY=your-production-key
```

---

## 📖 Documentation

- **[CHANGELOG.md](./CHANGELOG.md)** - Version history and changes
- **[BETA_RELEASE_SUMMARY.md](./BETA_RELEASE_SUMMARY.md)** - Comprehensive release checklist
- **[POLISH_ROADMAP.md](./POLISH_ROADMAP.md)** - P0/P1/P2 features roadmap
- **[FULL_STACK_LAUNCH_GUIDE.md](./FULL_STACK_LAUNCH_GUIDE.md)** - Complete deployment guide
- **[TEST_VERIFICATION_REPORT.md](./TEST_VERIFICATION_REPORT.md)** - Test results documentation
- **API Docs** - http://127.0.0.1:3738/docs (auto-generated OpenAPI)

---

## 🐛 Troubleshooting

### Common Port Issues

**Port 3738 already in use:**

```powershell
# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 3738).OwningProcess | Stop-Process

# Linux/Mac
lsof -ti:3738 | xargs kill -9
```

**Frontend port 3010 in use:**

```bash
# Use different port
npm run dev -- -p 3011
```

### Agent Not Responding

1. **Check Ollama is running:**

   ```bash
   curl http://127.0.0.1:11434/api/tags
   ```

2. **Verify agent directories exist:**

   ```bash
   ls -la agents/CEO/
   # Should contain: config.json, personas/, prompts/
   ```

3. **Check logs:**
   ```bash
   tail -f logs/app.log
   ```

### Tests Failing

```bash
# Reinstall in editable mode
pip install -e .

# Verify imports
python -c "from api.main import app; print('OK')"

# Run single test for debugging
pytest tests_flat/test_health.py -v
```

### Frontend Build Errors

```bash
# Clear Next.js cache
cd vboarder_frontend/nextjs_space
rm -rf .next
npm ci
npm run build
```

---

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch:** `git checkout -b feature/amazing-feature`
3. **Format code:** `make format && cd vboarder_frontend/nextjs_space && npm run format`
4. **Run tests:** `pytest -v && npm run build`
5. **Commit changes:** `git commit -m 'Add amazing feature'`
6. **Push to branch:** `git push origin feature/amazing-feature`
7. **Open Pull Request**

---

## 📋 Roadmap

### v0.9.0-beta.2 (Next Release)

- ✨ SSE streaming for real-time responses
- ✨ Message actions (copy, edit, regenerate)
- ✨ Enhanced error UX with toast notifications
- ✨ Persistent conversation threads (SQLite)
- ✨ Agent profile cards
- ✨ Request telemetry display

### v1.0.0 (Production Release)

- 🔐 Authentication system (JWT/OAuth)
- 🛡️ Rate limiting
- 📊 Prometheus metrics
- 🎨 Theme system (dark/light/high-contrast)
- ♿ Full accessibility (WCAG 2.1 AA)
- 🚀 Feature flags system

See [POLISH_ROADMAP.md](./POLISH_ROADMAP.md) for detailed implementation plans.

---

## 📄 License

MIT License - see [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM inference
- **FastAPI** - High-performance Python API framework
- **Next.js** - React framework for production
- **shadcn/ui** - Beautiful UI components

---

**Status:** ✅ Beta Release Ready
**Version:** 0.9.0-beta.1
**Last Updated:** October 14, 2025

**Need help?** Open an issue on GitHub or check the [documentation](./docs/)
