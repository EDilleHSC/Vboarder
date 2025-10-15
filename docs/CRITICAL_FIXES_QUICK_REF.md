# VBoarder Critical Fixes Quick Reference

**Issues:**

1. Missing persona.json files in agent directories
2. UTF-8 BOM in agent_registry.json
3. Backslash paths (Windows) in registry
4. Incomplete agent entries

**Impact:** All `/chat/{agent}` endpoints fail with "Agent role not found" or KeyError

---

## Quick Fix (Automated)

### One Command to Fix All Issues

```bash
cd /mnt/d/ai/projects/vboarder
source .venv-wsl/bin/activate
bash tools/ops/repair-all-agents.sh
```

This runs:

1. `rebuild-agents.py` - Creates missing persona.json, config.json, system prompts
2. `fix-registry-bom.py` - Removes UTF-8 BOM
3. `fix-registry-paths.py` - Converts backslashes to forward slashes
4. `verify-agent-setup.sh` - Confirms all agents configured
5. JSON validation

---

## Manual Fix (Step by Step)

### 1. Remove BOM

```bash
cd /mnt/d/ai/projects/vboarder
python3 tools/ops/fix-registry-bom.py
```

Or manually:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path("agent_registry.json")
b = p.read_bytes()
if b.startswith(b"\xef\xbb\xbf"):
    p.write_bytes(b[3:])
    print("✅ BOM removed from agent_registry.json")
else:
    print("ℹ️ No BOM found")
PY
```

### 2. Verify JSON

```bash
cat agent_registry.json | jq
```

Expected: Clean JSON array with 9 agents.

If still broken, re-encode:

```bash
iconv -f utf-8 -t utf-8 -c agent_registry.json -o agent_registry.json
```

### 3. Verify Agent Setup

```bash
bash tools/ops/verify-agent-setup.sh
```

This checks that all agents have required files:

- `config.json`
- `personas/system_detailed.txt`

### 4. Restart Backend

```bash
pkill -f uvicorn
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

### 5. Test Chat Endpoint

```bash
curl -s -X POST http://127.0.0.1:3738/chat/CTO \
  -H 'Content-Type: application/json' \
  -d '{"message":"Status report on beta readiness.","session_id":"live_test"}' | jq
```

Expected:

```json
{
  "agent": "CTO",
  "response": "System beta readiness confirmed...",
  "session_id": "live_test"
}
```

---

## Root Cause

**UTF-8 BOM** (bytes `EF BB BF`) is added by some Windows editors when saving UTF-8 files. JSON parsers don't expect it and fail.

**Prevention:**

- Use `.editorconfig` (already added) to enforce UTF-8 without BOM
- Use `git add` with `.gitattributes` (already configured)
- Verify with: `file agent_registry.json` (should say "UTF-8 Unicode text" not "UTF-8 Unicode (with BOM)")

---

## Tools Created

1. **`tools/ops/fix-registry-bom.py`** - Remove BOM from registry
2. **`tools/ops/verify-agent-setup.sh`** - Check all agents configured

Both are safe to run repeatedly.

---

## Adding Missing Agents

If any agent folder is missing (like CTO):

```bash
# Copy template from CEO
cp -r agents/CEO agents/CTO

# Update role in config
sed -i 's/"role": "CEO"/"role": "CTO"/' agents/CTO/config.json

# Update persona files manually
nano agents/CTO/personas/system_detailed.txt
```

---

## Validation Checklist

- [ ] BOM removed: `python3 tools/ops/fix-registry-bom.py`
- [ ] JSON valid: `cat agent_registry.json | jq`
- [ ] All agents exist: `bash tools/ops/verify-agent-setup.sh`
- [ ] Backend restarted
- [ ] Chat endpoint works: `curl .../chat/CTO`
- [ ] All 9 agents respond correctly

---

**After fixing, update `.gitattributes` to prevent BOM in future:**

```gitattributes
*.json text eol=lf encoding=utf-8
```

(Already configured in your `.gitattributes`!)
