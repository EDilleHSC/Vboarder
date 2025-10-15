# ⚡ VBoarder Quick Install Guide

**Get up and running in 5 minutes!**

---

## 🎯 Prerequisites

- ✅ Python 3.12+ installed
- ✅ Git installed
- ✅ VS Code installed (with WSL extension for Windows)
- ✅ WSL2 configured (Windows users)

---

## 🚀 Installation Steps

### Step 1: Install Pre-Commit Hooks (2 minutes)

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
make setup-hooks

# Or manually
pre-commit install
```

**What this does:**

- Auto-formats Python code (Black)
- Organizes imports (isort)
- Lints code (Ruff)
- Validates JSON/YAML
- Checks shell scripts
- Runs on every `git commit`

**Test it:**

```bash
# Run hooks manually (optional)
make pre-commit
```

---

### Step 2: Setup Environment Files (1 minute)

```bash
# Create development environment
make setup-dev

# Or manually
cp .env.example .env.development
```

**Then customize `.env.development`:**

```bash
# Edit with VS Code
code .env.development

# Key settings to verify:
# - LLM_MODE=local
# - LOCAL_URL=http://localhost:11434
# - BACKEND_PORT=3738
# - DEFAULT_MODEL=mixtral:latest
```

**For testing (optional):**

```bash
make setup-test
```

---

### Step 3: Open Workspace (30 seconds)

```bash
# Open multi-root workspace
code vboarder.code-workspace
```

**What you'll get:**

- 7 organized folders (Root, Backend, Agents, Frontend, Tools, Docs, Coord)
- Shared settings (Python, terminal, editor)
- 4 debug configurations
- Custom color theme
- Recommended extensions (will auto-prompt to install)

---

### Step 4: Install Dependencies (1 minute)

```bash
# Install Python packages
make install

# Or with dev dependencies
make install-dev
```

---

### Step 5: Start Backend (30 seconds)

```bash
# Quick start
make start

# Or backend only
make backend

# Or use VS Code task
Ctrl+Shift+P → Tasks: Run Task → "🚀 Start Backend"

# Or debug mode
F5 → Select "🚀 Backend API (Uvicorn)"
```

**Verify:**

- Backend running on http://127.0.0.1:3738
- Health check: http://127.0.0.1:3738/health
- API docs: http://127.0.0.1:3738/docs

---

## ✅ Validation (30 seconds)

```bash
# Run tests
make test

# Run smoke tests
make smoke-test

# Validate all systems
make validate
```

**Expected output:**

- ✅ 25/25 tests passing (pytest)
- ✅ 15/15 smoke tests passing
- ✅ All 9 agents operational

---

## 🎨 Optional: Enable Auto-Tasks

**Want backend to auto-start when opening workspace?**

1. Open `.vscode/settings.json`
2. Find the "Auto-Tasks" section
3. Uncomment these lines:

```json
"task.runOn": "folderOpen",
"task.autoDetect": "on"
```

4. Save and reload workspace

**Note:** Only enable if you always want the backend running!

---

## 🛠️ Makefile Commands (Reference)

### Quick Start

```bash
make start       # Backend + DevDash
make backend     # Backend only
make frontend    # Frontend only
make devdash     # DevDash only
```

### Testing

```bash
make test        # Run tests
make test-v      # Verbose tests
make test-cov    # With coverage
make smoke-test  # Smoke tests
make validate    # Full validation
```

### Code Quality

```bash
make lint        # Run linter
make lint-fix    # Auto-fix
make format      # Format code
make pre-commit  # Run hooks
```

### Development

```bash
make install     # Install deps
make install-dev # Install dev deps
make clean       # Remove cache
make clean-all   # Deep clean
```

---

## 🐛 Troubleshooting

### Pre-commit not working?

```bash
# Reinstall
pip install pre-commit --upgrade
pre-commit install --install-hooks
```

### Backend won't start?

```bash
# Check environment
cp .env.development .env
code .env

# Verify Python
which python
python --version  # Should be 3.12+

# Check dependencies
pip list | grep fastapi
```

### Tests failing?

```bash
# Clean and reinstall
make clean
make install
make test
```

### WSL issues? (Windows)

```bash
# Ensure WSL2 is default
wsl --set-default-version 2

# Restart WSL
wsl --shutdown
wsl

# Verify Python in WSL
wsl bash -c "python3 --version"
```

---

## 📚 Next Steps

**Explore Documentation:**

- `.vscode/QUICK_REFERENCE.md` - Command cheat sheet
- `.vscode/DESK_REFERENCE.md` - Print-friendly reference
- `docs/VSCODE_SETUP_GUIDE.md` - Complete VS Code setup
- `ELITE_SETUP_COMPLETE.md` - Elite features overview

**Learn the Workflow:**

```bash
# Daily workflow
code vboarder.code-workspace  # Open workspace
make backend                  # Start backend
# Make changes (auto-format on save)
git add .
git commit -m "feat: new feature"  # Pre-commit hooks run!
make test                     # Validate
```

**Explore Makefile:**

```bash
make help  # See all 28 commands
```

---

## 🎉 You're Done!

**VBoarder is now configured with:**

- ✅ Pre-commit hooks (auto code quality)
- ✅ Environment templates (dev/test)
- ✅ Multi-root workspace (organized folders)
- ✅ 28 Makefile commands (CLI shortcuts)
- ✅ Debug configurations (F5 to debug)
- ✅ Recommended extensions (auto-install)

**Time to build something amazing! 🚀**

---

**Need help?** Check `docs/` or run `make help`
