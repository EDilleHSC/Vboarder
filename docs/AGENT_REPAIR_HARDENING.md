# 🔒 Agent Repair System - Hardening Guide

**Version:** 1.1 (Hardened)
**Date:** October 14, 2025
**Status:** ✅ Production Ready

---

## 🎯 What Was Hardened

### 1. Garbage Directory Whitelist (Critical Fix)

**Problem:** Script was checking unnecessary directories like `__pycache__`, `venv`, `logs`

**Solution:** Case-based whitelist filter

```bash
# Inside the agent scanning loop
case "$role" in
    "__pycache__"|"default"|"venv"|"logs"|"tools"|"EXAMPLE"|"test_agent"|"agent_runtime"|"ops_agent")
        echo "   ⏭️  Skipping garbage dir: $role"
        continue
        ;;
esac
```

**Result:**

- ✅ Only scans actual agent directories (CEO, CTO, CFO, etc.)
- ✅ Skips 8 common garbage directories automatically
- ✅ Prevents false positives in registry
- ✅ Faster execution (fewer checks)

---

### 2. File Logging Support (Backend Enhancement)

**Problem:** Backend logs only went to console, hard to debug production issues

**Solution:** Added file handler to `api/main.py`

```python
# Ensure logs directory exists
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging with file handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "backend.log"),
        logging.StreamHandler()  # Keep console output too
    ]
)
```

**Result:**

- ✅ All backend logs written to `logs/backend.log`
- ✅ Console output still visible (dual logging)
- ✅ Persistent log file for debugging
- ✅ Auto-creates logs directory if missing

**Usage:**

```bash
# Watch logs in real-time
tail -f logs/backend.log

# Search for errors
grep ERROR logs/backend.log

# Last 50 lines
tail -50 logs/backend.log
```

---

### 3. Auto-Restart Option (Operational Enhancement)

**Problem:** After repair, manually restarting backend was tedious

**Solution:** Added optional `AUTO_RESTART` flag to repair script

```bash
# Optional: Auto-restart backend if AUTO_RESTART=true
if [ "${AUTO_RESTART:-false}" = "true" ]; then
    echo "🔁 AUTO_RESTART enabled - Restarting backend..."
    pkill -f "uvicorn api.main:app" 2>/dev/null || true
    sleep 1
    echo "   Starting uvicorn on port 3738..."
    nohup uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload > logs/uvicorn.log 2>&1 &
    echo "   ✅ Backend restarted (PID: $!)"
    echo "   📋 Logs: tail -f logs/uvicorn.log"
fi
```

**Result:**

- ✅ Optional flag (default: disabled)
- ✅ Gracefully kills old backend process
- ✅ Starts new backend in background
- ✅ Logs to `logs/uvicorn.log`
- ✅ Shows PID for process management

**Usage:**

```bash
# Standard repair (no restart)
bash tools/ops/repair-agents.sh

# Repair + auto-restart backend
AUTO_RESTART=true bash tools/ops/repair-agents.sh

# Dry-run with restart enabled (previews only)
DRY_RUN=true AUTO_RESTART=true bash tools/ops/repair-agents.sh
```

---

## 📊 Recovery Summary

### What Was Recovered

| Item              | Status        | Details                                                          |
| ----------------- | ------------- | ---------------------------------------------------------------- |
| Agent Registry    | ✅ Rebuilt    | 9 essential agents (CEO, CTO, CFO, COO, CMO, CLO, COS, SEC, AIR) |
| Garbage Filtering | ✅ Hardened   | 8 junk directories auto-skipped                                  |
| Missing Script    | ✅ Restored   | repair-agents.sh rebuilt and validated                           |
| File Logging      | ✅ Enabled    | Backend logs to logs/backend.log                                 |
| Auto-Restart      | ✅ Optional   | AUTO_RESTART flag added                                          |
| System State      | 💯 Beta-ready | No red flags, all tools operational                              |

### Directories Filtered (Whitelist)

```
__pycache__    → Python cache (skip)
default        → Legacy template (skip)
venv           → Virtual environment (skip)
logs           → Log files (skip)
tools          → Shared utilities (skip)
EXAMPLE        → Template directory (skip)
test_agent     → Test agent (skip)
agent_runtime  → Runtime files (skip)
ops_agent      → Operational agent (skip)
```

---

## 🚀 Usage Examples

### Basic Repair Flow

```bash
# 1. Preview what will be fixed
DRY_RUN=true bash tools/ops/repair-agents.sh

# 2. Execute repair
bash tools/ops/repair-agents.sh

# 3. Validate
cat agent_registry.json | jq '. | length'  # Should show 9
```

### Advanced: Repair + Restart + Validate

```bash
# Full automated flow
AUTO_RESTART=true bash tools/ops/repair-agents.sh && \
sleep 2 && \
bash tools/tests/run_smoke_beta.sh
```

### Production Process Manager Integration

```bash
# Option 1: systemd (Linux)
sudo systemctl restart vboarder-backend

# Option 2: PM2 (Cross-platform)
pm2 restart vboarder-backend

# Option 3: Supervisor
sudo supervisorctl restart vboarder-backend

# Option 4: Manual with make
make start_backend
```

---

## 🧪 Validation Checklist

After running hardened repair script:

- [ ] Registry contains exactly 9 agents
- [ ] No garbage directories in registry
- [ ] logs/backend.log exists and is writable
- [ ] Backend restarts without errors (if AUTO_RESTART=true)
- [ ] All 9 agents respond to chat requests
- [ ] Smoke tests pass (15/15)

**Validation Commands:**

```bash
# Check agent count
cat agent_registry.json | jq '. | length'

# Verify no garbage in registry
cat agent_registry.json | jq '.[].role' | grep -E "pycache|venv|logs|default"
# Should return empty (exit code 1)

# Check backend logs
ls -lh logs/backend.log

# Test all agents
bash tools/ops/test-all-agents.sh

# Full smoke test
bash tools/tests/run_smoke_beta.sh
```

---

## 🔍 Troubleshooting

### Issue: Garbage directories still in registry

**Solution:** Run repair script again with hardened version

```bash
bash tools/ops/repair-agents.sh
```

### Issue: Backend doesn't auto-restart

**Cause:** AUTO_RESTART flag not set or uvicorn not in PATH

**Solution:**

```bash
# Check if uvicorn is available
which uvicorn

# Use full path if needed
AUTO_RESTART=true bash tools/ops/repair-agents.sh
```

### Issue: Logs directory doesn't exist

**Cause:** Backend hasn't been started yet with new logging code

**Solution:**

```bash
# Create manually
mkdir -p logs

# Or let backend create it on first start
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

---

## 📚 Related Documentation

- **Complete Repair Guide:** `docs/AGENT_REPAIR_GUIDE.md`
- **CTO Shift Handoff:** `CTO_SHIFT_HANDOFF.md`
- **Smoke Test Script:** `tools/tests/run_smoke_beta.sh`
- **Validation Script:** `tools/ops/validate-all.sh`

---

## ✅ Best Practices

1. **Always dry-run first:** `DRY_RUN=true` before executing
2. **Check backups:** Verify `agent_registry.json.backup` exists
3. **Monitor logs:** `tail -f logs/backend.log` during operations
4. **Validate output:** Use `jq` to check JSON structure
5. **Keep whitelist updated:** Add new garbage dirs as needed

---

**Tags:** `#repair` `#hardening` `#v1.1` `#production` `#beta-ready`
