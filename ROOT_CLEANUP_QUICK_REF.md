# Root Cleanup - Quick Reference

## 🎯 What Was Created

### 3 Cleanup Scripts

1. **`tools/cleanup/audit-root-directory.sh`**

   - Analyzes current root structure
   - Shows file counts by type
   - Lists duplicates and candidates for archival
   - Provides cleanup recommendations

2. **`tools/cleanup/cleanup-root-structure.sh`**

   - Archives legacy files safely
   - Moves ~460 files to timestamped archive
   - Creates CLEANUP_FLAGS.md report
   - Supports DRY_RUN mode

3. **`tools/cleanup/enforce-root-structure.sh`**
   - Moves misfiled scripts to tools/ops/
   - Moves stray docs to docs/
   - Enforces v1.0 structure
   - Keeps root clean

### 1 Comprehensive Guide

4. **`docs/ROOT_CLEANUP_GUIDE.md`**
   - Complete walkthrough
   - Before/after comparison
   - Safety features
   - Recovery process

## ⚡ Quick Commands

### Step 1: Audit (See Current State)

```bash
bash tools/cleanup/audit-root-directory.sh
```

**Shows:**

- Total files in root: ~478
- Files by type (MD, SH, PS1, etc.)
- Duplicate documentation
- Scripts that should move
- Recommended actions

### Step 2: Dry Run (Preview Changes)

```bash
DRY_RUN=true bash tools/cleanup/cleanup-root-structure.sh
```

**Shows what would be moved without making changes**

### Step 3: Execute Cleanup

```bash
bash tools/cleanup/cleanup-root-structure.sh
```

**Creates:**

- `archive/root_legacy_YYYYMMDD_HHMMSS/` with ~460 files
- `CLEANUP_FLAGS.md` report

### Step 4: Enforce Structure

```bash
bash tools/cleanup/enforce-root-structure.sh
```

**Moves:**

- Scripts → tools/ops/
- Docs → docs/

### Step 5: Commit

```bash
git add .
git commit -m "🧹 Root cleanup v1.0"
```

## 📊 Expected Results

| Metric           | Before | After |
| ---------------- | ------ | ----- |
| Root .md files   | ~60    | 4     |
| Root scripts     | ~20    | 0     |
| Total root files | ~478   | ~15   |
| Archived files   | 0      | ~460  |

## ✅ What Stays in Root

**Documentation (4 files):**

- README.md
- START_HERE.md
- QUICK_START.md
- CHANGELOG.md (if exists)

**Configuration (~10 files):**

- .env.example, .gitignore, .gitattributes
- Makefile, pyproject.toml, requirements.txt
- pytest.ini, mypy.ini
- agent_registry.json
- vboarder.code-workspace

## 🗂️ What Gets Archived

**~460 files including:**

- Duplicate docs (FINAL_STATUS.md, Road map.MD, etc.)
- Legacy scripts (run*\*.sh, restart*\*.sh, etc.)
- Fix documentation (PATH_ISSUE_FIXED.md, etc.)
- Debug files (\*.log, New Text Document.txt)
- Duplicate registries (agent*registry*\*.json)

## 🔄 Recovery

```bash
# List archived files
ls archive/root_legacy_*/

# Restore specific file
cp archive/root_legacy_YYYYMMDD_HHMMSS/FILE.md .

# Full restore (emergency)
cp -r archive/root_legacy_YYYYMMDD_HHMMSS/* .
```

## 🎁 Benefits

1. **Faster Onboarding** - Clear, organized structure
2. **CI/CD Ready** - Standard paths for automation
3. **Reduced Conflicts** - Fewer root files
4. **Future-Proof** - Ready for packaging

## 📋 Safety Features

- ✅ DRY_RUN mode for preview
- ✅ Timestamped archives (no deletion)
- ✅ Detailed logging
- ✅ Fully reversible
- ✅ Git-friendly

## 🚀 Run Now

```bash
# Quick 3-command cleanup:

# 1. See what you have
bash tools/cleanup/audit-root-directory.sh

# 2. Preview cleanup
DRY_RUN=true bash tools/cleanup/cleanup-root-structure.sh

# 3. Execute (if preview looks good)
bash tools/cleanup/cleanup-root-structure.sh
```

## 📖 Full Documentation

See `docs/ROOT_CLEANUP_GUIDE.md` for:

- Complete file listings
- Customization options
- Troubleshooting
- Automation setup

---

**Status:** Ready to execute ✅
**Risk Level:** Low (all files archived, not deleted)
**Time Needed:** ~30 seconds
**Next Step:** Run audit to see current state
