#!/usr/bin/env bash
# VBoarder Root Cleanup - Safe & Reversible
# Creates archive, moves legacy files, enforces clean structure

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  VBoarder Root Cleanup - v1.0 Structure"
echo "═══════════════════════════════════════════════════════════════"
echo ""

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"

ARCHIVE_DIR="archive/root_legacy_$(date +%Y%m%d_%H%M%S)"
DRY_RUN=${DRY_RUN:-false}

echo "📂 Root directory: $ROOT"
echo "📦 Archive directory: $ARCHIVE_DIR"
echo "🔍 Dry run: $DRY_RUN"
echo ""

# Create archive directory
if [ "$DRY_RUN" = "false" ]; then
    mkdir -p "$ARCHIVE_DIR"
    echo "✅ Created archive: $ARCHIVE_DIR"
else
    echo "🔍 [DRY RUN] Would create: $ARCHIVE_DIR"
fi

# Function to safely move files
safe_move() {
    local pattern="$1"
    local description="$2"

    # Use array to handle files with spaces
    local files=()
    while IFS= read -r -d '' file; do
        files+=("$file")
    done < <(find . -maxdepth 1 -name "$pattern" -type f -print0 2>/dev/null || true)

    if [ ${#files[@]} -eq 0 ]; then
        echo "⏭️  No files matching: $pattern"
        return
    fi

    echo ""
    echo "📋 Moving $description:"
    for file in "${files[@]}"; do
        basename_file=$(basename "$file")
        echo "   • $basename_file"

        if [ "$DRY_RUN" = "false" ]; then
            mv "$file" "$ARCHIVE_DIR/"
        fi
    done

    echo "   ✅ Moved ${#files[@]} file(s)"
}

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Phase 1: Duplicate Documentation"
echo "═══════════════════════════════════════════════════════════════"

# Move duplicate roadmaps
safe_move "FINAL*.md" "FINAL status docs"
safe_move "FINAL*.Md" "FINAL status docs (mixed case)"
safe_move "*ROADMAP*.md" "Roadmap duplicates"
safe_move "*Road*map*.MD" "Roadmap duplicates (mixed case)"
safe_move "POLISH*.md" "Polish roadmaps"

# Move duplicate status files
safe_move "STATUS*.md" "Status files"
safe_move "*SUMMARY*.md" "Summary files"
safe_move "RELEASE_READY.md" "Release ready doc"
safe_move "READY_TO_LAUNCH.md" "Ready to launch doc"
safe_move "REORGANIZATION*.md" "Reorganization docs"
safe_move "VALIDATION*.md" "Validation docs"
safe_move "IMPLEMENTATION*.md" "Implementation docs"
safe_move "SESSION_SUMMARY.md" "Session summary"
safe_move "FIXES_APPLIED*.md" "Fixes applied reports"
safe_move "TEST_VERIFICATION*.md" "Test verification reports"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Phase 2: Script Sprawl"
echo "═══════════════════════════════════════════════════════════════"

# Move legacy runner scripts
safe_move "run_*.sh" "Run scripts"
safe_move "restart_*.sh" "Restart scripts"
safe_move "monitor_*.sh" "Monitor scripts"
safe_move "spring_activation.sh" "Spring activation"
safe_move "vboarder_guardian.sh" "Guardian script"
safe_move "start_backend.*" "Backend starters (should use Makefile)"

# Move duplicate PowerShell scripts
safe_move "*.ps1" "PowerShell scripts (move to scripts/)"
safe_move "*.bat" "Batch files"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Phase 3: Legacy Files & Debug Artifacts"
echo "═══════════════════════════════════════════════════════════════"

# Move logs and debug files
safe_move "*.log" "Log files"
safe_move "*debug*.txt" "Debug text files"
safe_move "New Text Document.txt" "Untitled text files"

# Move patch scripts
safe_move "Patch-*.ps1" "Patch scripts"
safe_move "*_FIX*.md" "Fix documentation"
safe_move "RUN_NOW*.md" "Urgent run docs"

# Move duplicate agent registries (keep only agent_registry.json)
safe_move "agent_registry_*.json" "Duplicate agent registries"
safe_move "webui_agents.json" "WebUI agents"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Phase 4: Duplicate README/Docs"
echo "═══════════════════════════════════════════════════════════════"

# Keep only README.md, move others
safe_move "README_NEW.md" "New README (duplicate)"
safe_move "REPO_STRUCTURE*.md" "Repo structure docs (move to docs/)"
safe_move "CHANGELOG*.md" "Changelogs (move to docs/)"
safe_move "RELEASE_NOTES*.md" "Release notes (move to docs/)"

# Move beta/dev docs to docs/
safe_move "BETA_*.md" "Beta docs (move to docs/)"
safe_move "DEVDASH_*.md" "DevDash docs (move to docs/)"
safe_move "*_PLAYBOOK.md" "Playbooks (move to docs/)"

# Move guide docs
safe_move "POWERSHELL_GUIDE.md" "PowerShell guide (move to docs/)"
safe_move "QUICK_*.md" "Quick guides (keep QUICK_START.md only)"
safe_move "START_BACKEND.md" "Start backend doc"
safe_move "PATH_ISSUE*.md" "Path issue docs"
safe_move "AGENT_REPAIR*.md" "Agent repair docs"
safe_move "REGISTRY_FIX*.md" "Registry fix docs"
safe_move "CLEANUP_FLAGS.md" "Cleanup flags (will recreate)"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Phase 5: Workspace & Config Files"
echo "═══════════════════════════════════════════════════════════════"

# Move workspace files (keep vboarder.code-workspace)
safe_move "To" "Misc 'To' file"
safe_move "wsl" "WSL file"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Phase 6: Create Clean Structure Documentation"
echo "═══════════════════════════════════════════════════════════════"

if [ "$DRY_RUN" = "false" ]; then
    cat > CLEANUP_FLAGS.md << 'EOF'
# VBoarder Root Cleanup - Completion Report

## Cleanup Date
$(date +"%Y-%m-%d %H:%M:%S")

## Actions Taken

### 📦 Archived Legacy Files
All legacy files moved to: `archive/root_legacy_YYYYMMDD_HHMMSS/`

### 🗂️ Current Root Structure (v1.0)

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
└── FRONTEND_PORT_UPDATE.md      # Recent updates
```

### 🎯 Kept in Root (Essential Files Only)

**Documentation:**
- README.md (primary)
- START_HERE.md (onboarding)
- QUICK_START.md (launch guide)
- FRONTEND_PORT_UPDATE.md (recent change)

**Scripts:**
- Makefile (build automation)
- Any single entry-point launcher (TBD)

**Configuration:**
- .env.example
- .gitignore, .gitattributes, .editorconfig
- pyproject.toml, requirements.txt
- pytest.ini, mypy.ini
- agent_registry.json (canonical)

### ✅ Benefits

1. **Faster Onboarding:** Clear structure, no clutter
2. **CI/CD Ready:** Standard paths for automation
3. **Reduced Conflicts:** Isolated documentation and logs
4. **Future-Proof:** Ready for packaging and distribution

### 🔄 Recovery

All moved files are preserved in `archive/root_legacy_*/`

To restore a file:
```bash
cp archive/root_legacy_YYYYMMDD_HHMMSS/<file> .
```

### 📋 Maintenance

Run cleanup periodically:
```bash
bash tools/cleanup/cleanup-root-structure.sh
```

Run with dry-run first:
```bash
DRY_RUN=true bash tools/cleanup/cleanup-root-structure.sh
```
EOF
    echo "✅ Created CLEANUP_FLAGS.md"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Cleanup Summary"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ "$DRY_RUN" = "false" ]; then
    MOVED_COUNT=$(find "$ARCHIVE_DIR" -type f 2>/dev/null | wc -l)
    echo "✅ Moved $MOVED_COUNT file(s) to archive"
    echo "📦 Archive location: $ARCHIVE_DIR"
    echo ""
    echo "🎯 Root directory is now clean and v1.0-ready!"
    echo ""
    echo "Next steps:"
    echo "  1. Review archived files: ls -la $ARCHIVE_DIR"
    echo "  2. Commit changes: git add . && git commit -m '🧹 Root cleanup v1.0'"
    echo "  3. Optional: Move select docs to docs/ folder"
else
    echo "🔍 DRY RUN COMPLETE"
    echo ""
    echo "To execute cleanup, run:"
    echo "  bash tools/cleanup/cleanup-root-structure.sh"
fi

echo ""
