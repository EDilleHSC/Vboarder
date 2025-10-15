# 🚀 VBoarder - Start Here!

**Version:** v0.9.0-beta.1
**Date:** October 14, 2025
**Status:** ✅ **PRODUCTION READY**

---

## ⚡ Quick Launch (2 Terminals)

### Terminal 1: Backend

```bash
wsl
cd /mnt/d/ai/projects/vboarder
source .venv-wsl/bin/activate
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

**Expected:** `INFO: Uvicorn running on http://127.0.0.1:3738`

### Terminal 2: Frontend

```bash
wsl
cd /mnt/d/ai/projects/vboarder/vboarder_frontend/nextjs_space
npm run dev
```

**Expected:** `Ready on http://localhost:3000`

---

## 🎯 Optional: Dev Dashboard

**Start Dashboard:**

```bash
wsl
cd /mnt/d/ai/projects/vboarder
source .venv-wsl/bin/activate
python3 tools/dev/devdash.py
```

**Open:** http://127.0.0.1:4545

**Features:**

- Start/stop backend and frontend from web UI
- View logs in real-time
- Quick links to all endpoints

---

## ✅ System Status

- ✅ **9 Agents Configured** (CEO, CTO, CFO, COO, CMO, CLO, COS, SEC, AIR)
- ✅ **Backend Operational** (port 3738)
- ✅ **Frontend Ready** (port 3000)
- ✅ **All Tests Passing** (25/25 pytest, 6/6 validation)
- ✅ **Registry Valid** (agent_registry.json - 9 entries)

---

## 🧪 Testing & Validation

### Test All 9 Agents

```bash
wsl
cd /mnt/d/ai/projects/vboarder
source .venv-wsl/bin/activate
bash tools/ops/test-all-agents.sh
```

**Expected:** All 9 agents respond ✅

### Run System Validation

```bash
bash tools/ops/validate-all.sh
```

**Expected:** 6/6 checks pass ✅

### Run Unit Tests

```bash
pytest -q
```

**Expected:** 25 passed ✅

---

## 🧹 Optional: Repository Cleanup

Clean up your root directory to v1.0 production standards:

### Step 1: Audit Current State

```bash
bash tools/cleanup/audit-root-directory.sh
```

Shows current file counts and cleanup recommendations.

### Step 2: Preview Cleanup (Safe)

```bash
DRY_RUN=true bash tools/cleanup/cleanup-root-structure.sh
```

Shows what would be archived without making changes.

### Step 3: Execute Cleanup

```bash
bash tools/cleanup/cleanup-root-structure.sh
```

Archives ~460 legacy files, keeps ~15 essential files.

**Full Guide:** See `ROOT_CLEANUP_SUMMARY.md` or `docs/ROOT_CLEANUP_GUIDE.md`

---

## 📚 Quick Reference

### Endpoints

- **Backend Health:** http://127.0.0.1:3738/health
- **Agents List:** http://127.0.0.1:3738/agents
- **Frontend UI:** http://localhost:3000
- **Dev Dashboard:** http://127.0.0.1:4545

### Chat with Agent (cURL)

```bash
curl -X POST http://127.0.0.1:3738/chat/CEO \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is our priority?","session_id":"test-123"}'
```

### Useful Scripts

| Script                                  | Purpose                    |
| --------------------------------------- | -------------------------- |
| `tools/ops/test-all-agents.sh`          | Test all 9 chat endpoints  |
| `tools/ops/validate-all.sh`             | Run system validation      |
| `tools/ops/check-location.sh`           | Verify correct directory   |
| `tools/ops/restart-backend.sh`          | Restart backend service    |
| `tools/dev/devdash.py`                  | Launch dev dashboard       |
| `tools/cleanup/audit-root-directory.sh` | Audit repository structure |

---

## 🆘 Troubleshooting

### Backend Won't Start?

**Check venv activation:**

```bash
wsl
cd /mnt/d/ai/projects/vboarder
source .venv-wsl/bin/activate
which python  # Should show .venv-wsl path
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

### Tests Failing?

**Ensure backend is running first:**

```bash
# Terminal 1: Start backend
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload

# Terminal 2: Run tests
pytest -q
```

### "No such file or directory" Errors?

**You're in wrong directory:**

```bash
bash tools/ops/check-location.sh  # Shows where you are
cd /mnt/d/ai/projects/vboarder     # Navigate to root
```

### Agent Test Script Stops Early?

**Fixed!** The script had a bug that caused early exit. Now tests all 9 agents.
See: `tools/ops/TEST_SCRIPT_FIX.md`

### Registry Issues?

**Rebuild registry:**

```bash
python3 tools/ops/rebuild-registry.py
```

### Complete Rebuild Needed?

**Run full repair:**

```bash
bash tools/ops/repair-all-agents.sh
```

**Full troubleshooting guide:** `docs/TROUBLESHOOTING.md`

---

## 🎓 Beta Testing

Ready to start beta testing? Follow the playbook:

```bash
cat docs/BETA_TEST_PLAYBOOK.md
```

**Create session log:**

```bash
cp docs/beta-notes/session-TEMPLATE.md \
   docs/beta-notes/session-$(date +%Y-%m-%d).md
```

---

## 📖 Documentation

| Document                     | Purpose                           |
| ---------------------------- | --------------------------------- |
| `README.md`                  | Project overview and architecture |
| `START_HERE.md`              | This guide - quick start          |
| `QUICK_START.md`             | Step-by-step launch guide         |
| `ROOT_CLEANUP_SUMMARY.md`    | Repository cleanup guide          |
| `FRONTEND_PORT_UPDATE.md`    | Port 3000 migration notes         |
| `docs/TROUBLESHOOTING.md`    | Complete troubleshooting          |
| `docs/BETA_TEST_PLAYBOOK.md` | Beta testing procedures           |
| `docs/DEV_DASHBOARD.md`      | DevDash documentation             |

---

## 🚀 You're Ready!

Your VBoarder system is fully operational and ready for:

1. ✅ **Development** - All services running
2. ✅ **Testing** - All tests passing
3. ✅ **Beta Testing** - Playbook ready
4. ✅ **Production** - Clean v1.0 structure (after cleanup)

**Next steps:**

1. Start backend and frontend (see Quick Launch above)
2. Test all agents: `bash tools/ops/test-all-agents.sh`
3. Optional: Clean up repository: `bash tools/cleanup/audit-root-directory.sh`
4. Begin beta testing: Follow `docs/BETA_TEST_PLAYBOOK.md`

**Need help?** See `docs/TROUBLESHOOTING.md` or run `bash tools/ops/check-location.sh`

---

_Last updated: October 14, 2025_
_VBoarder v0.9.0-beta.1_
