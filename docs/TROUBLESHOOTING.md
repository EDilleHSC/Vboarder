# 🆘 VBoarder Troubleshooting Guide

**Quick Reference for Common Issues**

---

## 🔍 Issue: "No such file or directory"

### Symptoms

```bash
bash tools/ops/repair-all-agents.sh
# bash: tools/ops/repair-all-agents.sh: No such file or directory
```

### Root Cause

You're in the **wrong directory** (probably the frontend directory instead of project root).

### Solution

#### 1. Check where you are:

```bash
pwd
```

If you see:

- `/mnt/d/ai/projects/vboarder/vboarder_frontend/...` ❌ **WRONG**
- `/mnt/d/ai/projects/vboarder/frontend/...` ❌ **WRONG**
- `/mnt/d/ai/projects/vboarder` ✅ **CORRECT**

#### 2. Navigate to project root:

```bash
cd /mnt/d/ai/projects/vboarder
```

#### 3. Verify location:

```bash
bash tools/ops/check-location.sh
```

Should show:

```
✅ You're in the correct directory (project root)
```

#### 4. Continue with commands:

```bash
source .venv-wsl/bin/activate
bash tools/ops/repair-all-agents.sh
```

---

## 🔍 Issue: Backend Won't Start

### Symptoms

```bash
uvicorn api.main:app --reload
# ModuleNotFoundError: No module named 'ollama'
# or
# ERROR: [Errno 98] Address already in use
```

### Root Cause

1. Virtual environment not activated (missing dependencies)
2. Port 3738 already in use by old process

### Solution

#### For "ModuleNotFoundError":

```bash
# Make sure you're in project root
cd /mnt/d/ai/projects/vboarder

# Activate venv
source .venv-wsl/bin/activate

# Verify activation (should show .venv-wsl path)
which python
# Should output: /mnt/d/ai/projects/vboarder/.venv-wsl/bin/python

# Start backend
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

#### For "Address already in use":

```bash
# Find the process
ps aux | grep uvicorn

# Kill it (replace XXXX with actual PID)
kill -9 XXXX

# Or use helper script
bash tools/ops/restart-backend.sh
```

---

## 🔍 Issue: Registry Empty or Invalid

### Symptoms

```bash
curl http://127.0.0.1:3738/agents
# {"agents": [], "count": 0}

cat agent_registry.json
# []
```

### Root Cause

Registry was cleared by path fixer or corrupted.

### Solution

```bash
# Navigate to project root
cd /mnt/d/ai/projects/vboarder

# Activate venv
source .venv-wsl/bin/activate

# Rebuild registry
python3 tools/ops/rebuild-registry.py

# Verify
cat agent_registry.json | jq '. | length'
# Should output: 9

# Restart backend
pkill -f uvicorn
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

---

## 🔍 Issue: Agent Files Missing

### Symptoms

```bash
bash tools/ops/verify-agent-setup.sh
# ❌ agents/CEO/persona.json not found
```

### Root Cause

Agent structure not rebuilt or files deleted.

### Solution

```bash
# Navigate to project root
cd /mnt/d/ai/projects/vboarder

# Activate venv
source .venv-wsl/bin/activate

# Rebuild agent structures
python3 tools/ops/rebuild-agents.py

# Rebuild registry
python3 tools/ops/rebuild-registry.py

# Verify
bash tools/ops/verify-agent-setup.sh
```

---

## 🔍 Issue: Tests Failing

### Symptoms

```bash
pytest -q
# FAILED tests/...
```

### Root Cause

Various - dependencies, import errors, registry issues.

### Solution

#### 1. Check you're in project root:

```bash
cd /mnt/d/ai/projects/vboarder
bash tools/ops/check-location.sh
```

#### 2. Activate venv:

```bash
source .venv-wsl/bin/activate
```

#### 3. Rebuild everything:

```bash
python3 tools/ops/rebuild-registry.py
bash tools/ops/verify-agent-setup.sh
```

#### 4. Run tests with verbose output:

```bash
pytest -v
```

#### 5. Check specific test:

```bash
pytest tests_flat/test_agent_imports.py -v
```

---

## 🔍 Issue: Permission Denied

### Symptoms

```bash
bash tools/ops/restart-backend.sh
# Permission denied
```

### Root Cause

Script not executable.

### Solution

```bash
# Make scripts executable
chmod +x tools/ops/*.sh

# Try again
bash tools/ops/restart-backend.sh
```

---

## 🔍 Issue: Virtual Environment Not Found

### Symptoms

```bash
source .venv-wsl/bin/activate
# No such file or directory
```

### Root Cause

1. Not in project root
2. Virtual environment not created

### Solution

#### Check location:

```bash
cd /mnt/d/ai/projects/vboarder
ls -la .venv-wsl
```

#### If .venv-wsl doesn't exist:

```bash
# Create it
python3 -m venv .venv-wsl

# Activate it
source .venv-wsl/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔍 Issue: jq Command Not Found

### Symptoms

```bash
cat agent_registry.json | jq
# jq: command not found
```

### Root Cause

jq not installed on system.

### Solution

```bash
# Install jq
sudo apt-get update
sudo apt-get install -y jq

# Or use Python as fallback
python3 -m json.tool agent_registry.json
```

---

## 📋 Quick Diagnostic Checklist

Run these in order to diagnose issues:

```bash
# 1. Check location
bash tools/ops/check-location.sh

# 2. Check venv
source .venv-wsl/bin/activate && which python

# 3. Check registry
cat agent_registry.json | python3 -m json.tool | grep -c "role"
# Should output: 9

# 4. Check agents
bash tools/ops/verify-agent-setup.sh

# 5. Check backend
curl http://127.0.0.1:3738/health

# 6. Run validation
bash tools/ops/validate-all.sh
```

---

## 🆘 Emergency Reset

If everything is broken, run this complete reset:

```bash
# 1. Navigate to project root
cd /mnt/d/ai/projects/vboarder

# 2. Activate venv
source .venv-wsl/bin/activate

# 3. Rebuild everything
python3 tools/ops/rebuild-agents.py
python3 tools/ops/rebuild-registry.py

# 4. Verify
bash tools/ops/verify-agent-setup.sh
cat agent_registry.json | jq '. | length'

# 5. Restart backend
bash tools/ops/restart-backend.sh

# 6. Test
curl http://127.0.0.1:3738/health
curl http://127.0.0.1:3738/agents | jq
```

---

## 📚 Getting Help

If issues persist:

1. Check `SESSION_SUMMARY.md` for complete session history
2. Review `docs/CRITICAL_FIXES_QUICK_REF.md` for known issues
3. Run full validation: `bash tools/ops/validate-all.sh`
4. Check backend logs in terminal where uvicorn is running

---

**Most Common Fix:**

```bash
cd /mnt/d/ai/projects/vboarder
source .venv-wsl/bin/activate
```

**Always start from the project root!** 📍
