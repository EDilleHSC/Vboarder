# VBoarder Tools & Scripts Summary

This document lists all the tools and scripts available in the VBoarder project.

## 🚀 Startup & Shutdown Scripts

### Bash/Linux/WSL

- **`start_vboarder.sh`** - Complete startup script for all VBoarder services

  - Starts Ollama (if not running)
  - Starts FastAPI backend on port 3738
  - Starts Next.js frontend on port 3001
  - Creates log files in `logs/`

- **`stop_vboarder.sh`** - Stops all VBoarder services
  - Kills backend and frontend processes
  - Option to stop Ollama (commented out by default)

### PowerShell/Windows

- **`start_vboarder.ps1`** - Windows version of startup script

  - Same functionality as bash version
  - Opens services in separate PowerShell windows

- **`stop_vboarder.ps1`** - Windows version of stop script
  - Stops all VBoarder services using port numbers

## 🔍 System Integrity Check

### Bash/Linux/WSL

- **`check_integrity.sh`** - Comprehensive system health check
  - Verifies all agent folders and files
  - Checks Ollama model availability
  - Tests backend API endpoints
  - Validates frontend status
  - Checks Python environment
  - Verifies Git repository status
  - Returns exit codes (0 = success, 1 = failure)

### PowerShell/Windows

- **`check_integrity.ps1`** - Windows version of integrity check
  - Same functionality as bash version
  - Uses PowerShell-native commands

## � Deep System Inventory

- **`generate_inventory_report.py`** - Comprehensive system audit script
  - Generates detailed Markdown report (`vboarder_inventory.md`)
  - Checks 100+ system components
  - Validates all agent configurations
  - Lists installed packages and versions
  - Detects broken symlinks
  - Reports on Git status and tags
  - Verifies Ollama installation and models
  - Provides summary statistics
  - See `docs/INVENTORY_REPORT.md` for full documentation

## �📚 Documentation

- **`.github/copilot-instructions.md`** - AI coding agent guide

  - Architecture overview
  - Developer workflows
  - Key patterns and conventions
  - Testing guidelines

- **`STARTUP_GUIDE.md`** - Quick start and troubleshooting
  - Startup instructions
  - What gets started
  - Log locations
  - Troubleshooting tips

## 🛠️ Core API Files (Fixed)

- **`api/simple_connector.py`**

  - ✅ Fixed async/await issues
  - ✅ All `_build_system_prompt()` calls use `await`
  - ✅ Converted `chat()` to async
  - ✅ Removed duplicate function definitions

- **`api/main.py`**

  - ✅ Updated to await async connector methods
  - ✅ Added coroutine debug checks
  - ✅ Fixed line length issues

- **`api/utils/logger.py`**

  - ✅ Fixed UTF-8 encoding issues
  - ✅ Removed BOM characters

- **`api/utils/__init__.py`**
  - ✅ Added UTF-8 encoding declaration

## 📋 Usage Examples

### Check System Health

```bash
# Linux/WSL
bash check_integrity.sh

# Windows
.\check_integrity.ps1
```

### Start VBoarder

```bash
# Linux/WSL
bash start_vboarder.sh

# Windows
.\start_vboarder.ps1
```

### Stop VBoarder

```bash
# Linux/WSL
bash stop_vboarder.sh

# Windows
.\stop_vboarder.ps1
```

### Monitor Logs

```bash
# Backend
tail -f logs/backend.log

# Frontend
tail -f logs/frontend.log
```

### Test API

```bash
# Health check
curl http://127.0.0.1:3738/health

# List agents
curl http://127.0.0.1:3738/agents

# Chat with CEO
curl -X POST http://127.0.0.1:3738/chat/CEO \
  -H "Content-Type: application/json" \
  -d '{"message":"What are our priorities?"}'
```

## 🎯 Exit Codes

### Integrity Check Scripts

- `0` - All checks passed (or only warnings)
- `1` - Critical failures detected

### Startup Scripts

- Scripts run in background, check logs for status

## 📝 Notes

- All bash scripts should be executed from the project root directory
- PowerShell scripts require execution policy set appropriately
- Logs are automatically created in `logs/` directory
- Backend runs on port 3738, frontend on port 3001
- Ollama should be installed and models pulled before running

## 🔄 Recent Changes

- Fixed all async/await coroutine issues
- Added comprehensive system integrity checks
- Created cross-platform startup/shutdown scripts
- Fixed UTF-8 encoding in Python files
- Updated AI coding agent instructions

## 🆘 Getting Help

If you encounter issues:

1. Run the integrity check first: `bash check_integrity.sh`
2. Review logs in `logs/backend.log` and `logs/frontend.log`
3. Check the `STARTUP_GUIDE.md` for troubleshooting tips
4. Ensure all dependencies are installed: `pip install -r requirements.txt`
5. Verify Ollama is running: `ollama list`

---

Last updated: October 14, 2025
