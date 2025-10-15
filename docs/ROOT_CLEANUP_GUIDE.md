# VBoarder Root Cleanup - v1.0 Structure Guide

## 🎯 Overview

This guide walks you through cleaning up VBoarder's root directory to achieve a production-ready v1.0 structure.

**Current State:** ~478 top-level files, 70 directories
**Target State:** ~15 essential files, clean organization

## 📋 Quick Start

### Step 1: Audit Current State

```bash
# Run audit to see what you have
bash tools/cleanup/audit-root-directory.sh
```

This shows:

- File counts by type
- Duplicate documentation
- Scripts that could move to tools/
- Configuration files to keep
- Cleanup recommendations

### Step 2: Dry Run Cleanup

```bash
# See what would be moved (no changes made)
DRY_RUN=true bash tools/cleanup/cleanup-root-structure.sh
```

Reviews all files that would be archived.

### Step 3: Execute Cleanup

```bash
# Actually move files to archive
bash tools/cleanup/cleanup-root-structure.sh
```

Creates `archive/root_legacy_YYYYMMDD_HHMMSS/` with all moved files.

### Step 4: Enforce Structure

```bash
# Move any remaining misfiled items
bash tools/cleanup/enforce-root-structure.sh
```

Ensures scripts and docs are in correct folders.

### Step 5: Commit Changes

```bash
git add .
git commit -m "🧹 Root cleanup v1.0 - organized structure"
```

## 🗂️ Target Structure (v1.0)

```
vboarder/
├── api/                         # Backend FastAPI
├── agents/                      # All agent logic (9 agents)
├── coord/                       # Orchestration
├── data/                        # Persistent state
├── docs/                        # Documentation hub
├── scripts/                     # High-level utility scripts
├── tools/                       # Developer tools
│   ├── ops/                     # Operations scripts
│   ├── dev/                     # Development tools
│   ├── cleanup/                 # Cleanup utilities
│   └── inventory/               # Inventory scripts
├── vboarder_frontend/           # Next.js UI
├── vboarder_reports/            # Reports & logs
├── logs/                        # Raw logs
├── archive/                     # Historical files
│
├── .env.example                 # Environment template
├── .gitattributes               # Git line endings
├── .gitignore                   # Git ignore rules
├── .editorconfig                # Editor configuration
├── Makefile                     # Build automation
├── pyproject.toml               # Python project config
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
├── mypy.ini                     # Type checking config
├── agent_registry.json          # Agent registry (canonical)
│
├── README.md                    # Primary documentation
├── START_HERE.md                # Quick start guide
├── QUICK_START.md               # Launch instructions
└── CHANGELOG.md                 # Version history
```

## 🧰 What Gets Archived

### Duplicate Documentation (~40 files)

- ✅ `FINAL_STATUS.md`, `FINAL RAOD MAP.Md`, etc.
- ✅ `Road map.MD`, `POLISH_ROADMAP.md`
- ✅ `STATUS.md`, `SESSION_SUMMARY.md`
- ✅ `RELEASE_READY.md`, `READY_TO_LAUNCH.md`
- ✅ `REORGANIZATION_COMPLETED.md`
- ✅ `VALIDATION_NEXT_STEPS.md`
- ✅ `IMPLEMENTATION_STATUS.md`
- ✅ `FIXES_APPLIED_REPORT.md`
- ✅ `TEST_VERIFICATION_REPORT.md`
- ✅ `README_NEW.md` (keep README.md only)
- ✅ `BETA_RELEASE_SUMMARY.md` → move to docs/
- ✅ `DEVDASH_RELEASE_NOTES.md` → move to docs/

### Script Sprawl (~20 files)

- ✅ `run_*.sh` (run_all.sh, run_backend.sh, etc.)
- ✅ `restart_*.sh` (restart_vboarder.sh)
- ✅ `monitor_*.sh` (monitor_vboarder\*.sh)
- ✅ `spring_activation.sh`
- ✅ `vboarder_guardian.sh`
- ✅ `start_backend.*` (use Makefile instead)
- ✅ `start_full_stack.sh`
- ✅ `*.ps1` files (Patch-AgentDiscovery.ps1, setup_vboarder_env.ps1)
- ✅ `*.bat` files (start_backend.bat)

### Legacy Files

- ✅ `*.log` files (debug logs)
- ✅ `New Text Document.txt`
- ✅ `To` (misc file)
- ✅ `wsl` (misc file)
- ✅ Duplicate registries (`agent_registry_*.json`, `webui_agents.json`)

### Fix/Patch Documentation

- ✅ `PATH_ISSUE_FIXED.md`
- ✅ `AGENT_REPAIR_STATUS.md`
- ✅ `REGISTRY_FIX_URGENT.md`
- ✅ `RUN_NOW_FIX_REGISTRY.md`
- ✅ `CLEANUP_FLAGS.md` (will be recreated)

## 📁 What Stays in Root

### Essential Documentation (4 files)

- ✅ `README.md` - Primary documentation
- ✅ `START_HERE.md` - Onboarding guide
- ✅ `QUICK_START.md` - Launch instructions
- ✅ `CHANGELOG.md` - Version history (if exists)

### Configuration Files (~10 files)

- ✅ `.env.example`
- ✅ `.gitignore`, `.gitattributes`, `.editorconfig`
- ✅ `Makefile`
- ✅ `pyproject.toml`, `requirements.txt`
- ✅ `pytest.ini`, `mypy.ini`
- ✅ `agent_registry.json` (canonical)
- ✅ `vboarder.code-workspace` (VS Code workspace)

### Project Metadata

- ✅ `VERSION`
- ✅ `LICENSE` (if exists)
- ✅ `CONTRIBUTING.md` (if exists)

## 🔄 Recovery Process

All archived files are preserved and can be restored:

```bash
# List archived files
ls -la archive/root_legacy_YYYYMMDD_HHMMSS/

# Restore a specific file
cp archive/root_legacy_YYYYMMDD_HHMMSS/SOME_FILE.md .

# Restore everything (emergency)
cp -r archive/root_legacy_YYYYMMDD_HHMMSS/* .
```

## 🎁 Benefits After Cleanup

### 1. Faster Onboarding

- New developers see clean, organized structure
- No confusion about which README to read
- Clear separation of concerns

### 2. CI/CD Integration

- Standard paths for automation
- Predictable file locations
- Easy to script deployments

### 3. Reduced Merge Conflicts

- Fewer top-level files
- Documentation isolated in docs/
- Scripts organized in tools/

### 4. Future-Proof

- Ready for PyPI packaging (pyproject.toml)
- Docker-friendly structure
- Follows Python project best practices

## 📊 Before & After Comparison

| Metric              | Before | After |
| ------------------- | ------ | ----- |
| Top-level .md files | ~60    | 4     |
| Top-level scripts   | ~20    | 0-1   |
| Configuration files | ~10    | ~10   |
| Total root files    | ~478   | ~15   |
| Archived files      | 0      | ~460  |

## 🚀 Automation for Future

### Auto-Enforcement (Optional)

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Auto-enforce structure on commit
bash tools/cleanup/enforce-root-structure.sh
git add -A
```

### Periodic Cleanup

Run monthly:

```bash
# Audit current state
bash tools/cleanup/audit-root-directory.sh

# Clean if needed
bash tools/cleanup/cleanup-root-structure.sh
```

## 🔍 Safety Features

### All Scripts Use:

- ✅ Dry run mode (`DRY_RUN=true`)
- ✅ Timestamped archives
- ✅ Safe move (no deletion)
- ✅ Detailed logging
- ✅ Reversible operations

### Before Running:

1. Commit current work (`git commit`)
2. Run audit first
3. Use dry run mode
4. Review what will be moved
5. Then execute cleanup

## 📝 Custom Exclusions

Edit `tools/cleanup/cleanup-root-structure.sh` to exclude specific files:

```bash
# Add to script before moving
if [[ "$basename_file" == "IMPORTANT_FILE.md" ]]; then
    echo "   ⏭️  Skipping: $basename_file (excluded)"
    continue
fi
```

## ✅ Verification Checklist

After cleanup:

- [ ] All tests pass: `pytest -q`
- [ ] Backend starts: `uvicorn api.main:app --port 3738`
- [ ] Frontend starts: `cd vboarder_frontend/nextjs_space && npm run dev`
- [ ] DevDash works: `python3 tools/dev/devdash.py`
- [ ] All agents respond: `bash tools/ops/test-all-agents.sh`
- [ ] Git status clean: `git status`
- [ ] Archive created: `ls -la archive/`

## 🆘 Troubleshooting

### "Permission denied" errors

```bash
chmod +x tools/cleanup/*.sh
```

### "Directory not empty" errors

Scripts use safe `mv`, won't fail on existing files

### Want to undo cleanup?

```bash
# Restore from archive
cp -r archive/root_legacy_YYYYMMDD_HHMMSS/* .
```

### Script not found

```bash
# Ensure you're in project root
cd /mnt/d/ai/projects/vboarder
bash tools/cleanup/audit-root-directory.sh
```

## 📞 Support

- See `docs/TROUBLESHOOTING.md` for common issues
- Run audit for current state: `bash tools/cleanup/audit-root-directory.sh`
- All operations are logged in `CLEANUP_FLAGS.md` after execution

---

**Ready to clean?** Start with the audit:

```bash
bash tools/cleanup/audit-root-directory.sh
```
