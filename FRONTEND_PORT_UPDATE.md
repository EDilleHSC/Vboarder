# Frontend Port Update - Port 3010 → 3000

## ✅ Changes Made

### 1. Package.json Updated

**File:** `vboarder_frontend/nextjs_space/package.json`

**Changed:**

```json
"scripts": {
  "dev": "next dev -p 3000",     // was: -p 3010
  "start": "next start -p 3000"  // was: -p 3010
}
```

### 2. DevDash Updated

**File:** `tools/dev/devdash.py`

**Changed:**

```python
FRONTEND_PORT = int(os.getenv("VB_FRONTEND_PORT", 3000))  # was: 3010
```

## 📝 Documentation Files That Reference 3010

The following files still reference port 3010 and should be updated to 3000:

- README.md
- README_NEW.md
- START_HERE.md
- QUICK_COMMANDS.md
- QUICK_START.md
- RELEASE_READY.md
- BETA_RELEASE_SUMMARY.md
- REPO_STRUCTURE_NEW.md
- docs/DEV_DASHBOARD.md
- docs/DEVDASH_QUICKSTART.md
- docs/BETA_TEST_PLAYBOOK.md
- DEVDASH_RELEASE_NOTES.md
- .github/pull_request_template.md

## 🔄 How to Apply

### Option A: Use the Update Script

```bash
python3 tools/ops/update-frontend-port.py
```

### Option B: Manual Find & Replace

In VS Code:

1. Press `Ctrl+Shift+H` (Find and Replace in Files)
2. Find: `3010`
3. Replace: `3000`
4. Files to include: `*.md`
5. Review each match before replacing

### Common Patterns to Replace:

- `port 3010` → `port 3000`
- `localhost:3010` → `localhost:3000`
- `127.0.0.1:3010` → `127.0.0.1:3000`
- `-p 3010` → `-p 3000`
- `VB_FRONTEND_PORT=3010` → `VB_FRONTEND_PORT=3000`
- `FE 3010` → `FE 3000`

## 🚀 Restart Frontend

After updating, restart the frontend:

### From DevDash

1. Visit http://127.0.0.1:4545
2. Click "Stop" for Frontend (if running)
3. Click "Start" for Frontend
4. Frontend now runs on **port 3000**

### From Terminal

```bash
cd vboarder_frontend/nextjs_space
npm run dev
# Now serves on http://localhost:3000
```

## ✅ Verification

After restart, frontend should be accessible at:

- **New:** http://localhost:3000 ✅
- **Old:** ~~http://localhost:3010~~ ❌ (no longer used)

Backend remains on:

- http://127.0.0.1:3738 (unchanged)

DevDash runs on:

- http://127.0.0.1:4545 (unchanged)

## 📋 Summary

| Service            | Old Port | New Port | Status         |
| ------------------ | -------- | -------- | -------------- |
| Backend (Uvicorn)  | 3738     | 3738     | Unchanged ✅   |
| Frontend (Next.js) | 3010     | **3000** | **Updated** ✅ |
| DevDash (Flask)    | 4545     | 4545     | Unchanged ✅   |

## 🎯 Next Steps

1. **Optional:** Run `python3 tools/ops/update-frontend-port.py` to update all docs
2. **Required:** Restart frontend from devdash or terminal
3. **Verify:** Visit http://localhost:3000

Your VBoarder frontend will now run on the standard port 3000! 🎉
