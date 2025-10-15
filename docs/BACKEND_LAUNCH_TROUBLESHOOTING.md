# Backend Launch Troubleshooting Guide

## Issue: "No Python at '/usr/bin\python.exe'"

This error indicates that the virtual environment scripts have incorrect shebang lines (Unix paths instead of Windows paths).

## ✅ Solution 1: Recreate Virtual Environment (RECOMMENDED)

```powershell
# 1. Navigate to project
cd D:\ai\projects\vboarder

# 2. Deactivate current venv (if active)
deactivate

# 3. Remove corrupted venv
Remove-Item -Path .venv -Recurse -Force

# 4. Create fresh venv
python -m venv .venv

# 5. Activate it
.\.venv\Scripts\Activate.ps1

# 6. Install dependencies
pip install -r requirements.txt

# 7. Start backend
python -m uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

## ✅ Solution 2: Use System Python Directly

If recreating venv doesn't work, use system Python:

```powershell
cd D:\ai\projects\vboarder

# Install dependencies globally (or in system Python)
pip install fastapi uvicorn ollama pydantic python-dotenv aiofiles asyncpg

# Start backend
python -m uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

## ✅ Solution 3: Use WSL

If Windows paths are problematic, use WSL:

```bash
cd /mnt/d/ai/projects/vboarder

# Create venv in WSL
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate

# Install deps
pip install -r requirements.txt

# Start backend
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

## ✅ Solution 4: Manual Startup (Quick Fix)

Create a simple startup script that bypasses venv scripts:

```powershell
# File: quick_start.ps1
$pythonExe = "python"  # Or full path like C:\Python311\python.exe
cd D:\ai\projects\vboarder
& $pythonExe -m uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

Run it:

```powershell
.\quick_start.ps1
```

## 🧪 Verify Ollama is Installed

```powershell
python -c "import ollama; print('✓ ollama installed')"
```

If not installed:

```powershell
pip install ollama
```

## 🔍 Check Current Python

```powershell
# Check which Python is being used
Get-Command python | Select-Object Source

# Check Python version
python --version

# Check if uvicorn is installed
python -m uvicorn --version
```

## 📦 Verify All Dependencies

```powershell
python -c "import fastapi, uvicorn, ollama, pydantic, aiofiles, asyncpg; print('All imports OK')"
```

## 🚀 Once Backend Starts Successfully

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:3738 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Test with:

```powershell
curl http://127.0.0.1:3738/health
```

Expected response:

```json
{ "status": "ok" }
```

## 📝 Root Cause

The error "No Python at '/usr/bin\python.exe'" occurs when:

1. Virtual environment was created in WSL or copied from Linux
2. Virtual environment scripts have Unix shebang lines: `#!/usr/bin/python.exe`
3. Windows can't interpret Unix paths

**Fix:** Recreate venv in Windows OR use WSL consistently.

## 🎯 Next Steps After Backend Runs

1. Start frontend:

```powershell
cd D:\ai\projects\vboarder\vboarder_frontend\nextjs_space
npm run dev
```

2. Test integration:

- Open http://localhost:3000
- Select CEO agent
- Send test message: "Hello, what can you help with?"
- Verify streaming response appears

## 📞 Still Having Issues?

Check:

- Python installation: `python --version` (should be 3.10+)
- pip works: `pip --version`
- FastAPI installed: `python -c "import fastapi"`
- Ollama installed: `python -c "import ollama"`
- Port 3738 available: `netstat -an | findstr 3738`

If port is occupied:

```powershell
# Use different port
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload

# Update frontend .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```
