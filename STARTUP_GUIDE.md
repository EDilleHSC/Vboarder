# VBoarder Startup Scripts

This directory contains scripts to easily start and stop the VBoarder multi-agent system.

## Quick Start

### For WSL/Linux Users:

```bash
# Check system integrity first
bash check_integrity.sh

# Start everything
bash start_vboarder.sh

# Stop everything
bash stop_vboarder.sh
```

### For Windows/PowerShell Users:

```powershell
# Check system integrity first
.\check_integrity.ps1

# Start everything
.\start_vboarder.ps1

# Stop everything
.\stop_vboarder.ps1
```

## What Gets Started

1. **Ollama** - Local LLM inference server (if not already running)
2. **Backend API** - FastAPI server on http://127.0.0.1:3738
3. **Frontend** - Next.js dev server on http://localhost:3001 (if available)

## Logs

Logs are written to the `logs/` directory:

- `logs/backend.log` - Backend API logs
- `logs/frontend.log` - Frontend dev server logs

To monitor logs in real-time:

```bash
# Backend
tail -f logs/backend.log

# Frontend
tail -f logs/frontend.log
```

## Troubleshooting

### Port Already in Use

If you get a "port already in use" error, run the stop script first:

```bash
bash stop_vboarder.sh  # or .\stop_vboarder.ps1
```

### Python Virtual Environment Not Found

Make sure you've created a virtual environment:

```bash
# WSL/Linux
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install -r requirements.txt

# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Ollama Not Found

Install Ollama from https://ollama.ai and ensure it's in your PATH.

## Manual Start (Alternative)

If the scripts don't work, you can start manually:

```bash
# Terminal 1: Backend
source .venv-wsl/bin/activate  # or .\.venv\Scripts\Activate.ps1
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload

# Terminal 2: Frontend (optional)
cd vboarder_frontend/nextjs_space
npm run dev -- -p 3001
```

## Health Check

After starting, verify everything is running:

```bash
curl http://127.0.0.1:3738/health
# Should return: {"status":"ok"}
```

Or visit http://127.0.0.1:3738/health in your browser.
