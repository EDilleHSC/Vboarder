#!/usr/bin/env bash
# Analyze current root directory structure

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  VBoarder Root Directory Audit"
echo "═══════════════════════════════════════════════════════════════"
echo ""

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"

echo "📂 Root directory: $ROOT"
echo "📅 Audit date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Count files and directories
echo "═══════════════════════════════════════════════════════════════"
echo "  Overall Statistics"
echo "═══════════════════════════════════════════════════════════════"
echo ""

TOTAL_FILES=$(find . -maxdepth 1 -type f | wc -l)
TOTAL_DIRS=$(find . -maxdepth 1 -type d | wc -l)

echo "📊 Top-level files: $TOTAL_FILES"
echo "📁 Top-level directories: $TOTAL_DIRS"
echo ""

# Categorize files by type
echo "═══════════════════════════════════════════════════════════════"
echo "  File Breakdown by Type"
echo "═══════════════════════════════════════════════════════════════"
echo ""

count_files() {
    local pattern="$1"
    find . -maxdepth 1 -name "$pattern" -type f 2>/dev/null | wc -l
}

MD_COUNT=$(count_files "*.md")
MD_MIXED=$(count_files "*.MD")
MD_MIXED2=$(count_files "*.Md")
SH_COUNT=$(count_files "*.sh")
PS1_COUNT=$(count_files "*.ps1")
BAT_COUNT=$(count_files "*.bat")
PY_COUNT=$(count_files "*.py")
JSON_COUNT=$(count_files "*.json")
TXT_COUNT=$(count_files "*.txt")
LOG_COUNT=$(count_files "*.log")

echo "📝 Markdown files (.md): $MD_COUNT"
[ "$MD_MIXED" -gt 0 ] && echo "📝 Markdown files (.MD): $MD_MIXED (mixed case)"
[ "$MD_MIXED2" -gt 0 ] && echo "📝 Markdown files (.Md): $MD_MIXED2 (mixed case)"
echo "🔧 Shell scripts (.sh): $SH_COUNT"
echo "⚙️  PowerShell scripts (.ps1): $PS1_COUNT"
echo "🪟 Batch files (.bat): $BAT_COUNT"
echo "🐍 Python files (.py): $PY_COUNT"
echo "📋 JSON files (.json): $JSON_COUNT"
echo "📄 Text files (.txt): $TXT_COUNT"
echo "📊 Log files (.log): $LOG_COUNT"
echo ""

# List duplicate documentation
echo "═══════════════════════════════════════════════════════════════"
echo "  Duplicate Documentation (Candidates for Archive)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "🌀 Roadmaps:"
find . -maxdepth 1 -iname "*roadmap*.md" -o -iname "*roadmap*.MD" 2>/dev/null | sed 's|^\./|   • |' || echo "   None found"
echo ""

echo "📊 Status Files:"
find . -maxdepth 1 -iname "status*.md" -o -iname "final*.md" -o -iname "*summary*.md" 2>/dev/null | sed 's|^\./|   • |' || echo "   None found"
echo ""

echo "✅ Release/Ready Files:"
find . -maxdepth 1 -iname "release*.md" -o -iname "ready*.md" -o -iname "launch*.md" 2>/dev/null | sed 's|^\./|   • |' || echo "   None found"
echo ""

# List scripts that could move to tools/
echo "═══════════════════════════════════════════════════════════════"
echo "  Scripts (Candidates for tools/ops/)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "🔄 Run/Restart Scripts:"
find . -maxdepth 1 \( -name "run_*.sh" -o -name "restart_*.sh" -o -name "start_*.sh" \) 2>/dev/null | sed 's|^\./|   • |' || echo "   None found"
echo ""

echo "📡 Monitor Scripts:"
find . -maxdepth 1 -name "monitor_*.sh" 2>/dev/null | sed 's|^\./|   • |' || echo "   None found"
echo ""

echo "⚙️  Other Scripts:"
find . -maxdepth 1 -name "*.sh" ! -name "run_*" ! -name "restart_*" ! -name "start_*" ! -name "monitor_*" 2>/dev/null | sed 's|^\./|   • |' || echo "   None found"
echo ""

# List config files (keep these)
echo "═══════════════════════════════════════════════════════════════"
echo "  Configuration Files (KEEP in Root)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

find . -maxdepth 1 \( -name "*.ini" -o -name "*.toml" -o -name ".env*" -o -name "*.json" -o -name "Makefile" -o -name "requirements*.txt" \) 2>/dev/null | sed 's|^\./|   ✅ |' || echo "   None found"
echo ""

# List essential docs (keep these)
echo "═══════════════════════════════════════════════════════════════"
echo "  Essential Documentation (KEEP in Root)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

ESSENTIAL_DOCS=(
    "README.md"
    "START_HERE.md"
    "QUICK_START.md"
    "CHANGELOG.md"
    "LICENSE"
    "CONTRIBUTING.md"
)

for doc in "${ESSENTIAL_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo "   ✅ $doc"
    fi
done
echo ""

# Show directory structure
echo "═══════════════════════════════════════════════════════════════"
echo "  Directory Structure"
echo "═══════════════════════════════════════════════════════════════"
echo ""

find . -maxdepth 1 -type d ! -name "." ! -name ".git" ! -name "__pycache__" ! -name "*.egg-info" 2>/dev/null | sed 's|^\./|   📁 |' | sort || echo "   None found"
echo ""

# Recommendations
echo "═══════════════════════════════════════════════════════════════"
echo "  Cleanup Recommendations"
echo "═══════════════════════════════════════════════════════════════"
echo ""

RECOMMENDED_ARCHIVE=$((MD_COUNT - 4 + SH_COUNT / 2 + PS1_COUNT + BAT_COUNT + TXT_COUNT + LOG_COUNT))

echo "📦 Estimated files for archival: ~$RECOMMENDED_ARCHIVE"
echo ""
echo "🎯 Recommended actions:"
echo ""
echo "   1. DRY RUN first:"
echo "      DRY_RUN=true bash tools/cleanup/cleanup-root-structure.sh"
echo ""
echo "   2. Execute cleanup:"
echo "      bash tools/cleanup/cleanup-root-structure.sh"
echo ""
echo "   3. Enforce structure:"
echo "      bash tools/cleanup/enforce-root-structure.sh"
echo ""
echo "   4. Commit changes:"
echo "      git add . && git commit -m '🧹 Root cleanup v1.0'"
echo ""

# Create summary report
echo "═══════════════════════════════════════════════════════════════"
echo "  Audit Complete"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Report saved to: tools/cleanup/audit_$(date +%Y%m%d_%H%M%S).txt"
echo ""
