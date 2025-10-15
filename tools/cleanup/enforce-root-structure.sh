#!/usr/bin/env bash
# Enforce VBoarder Root Structure - Move misfiled items to correct locations

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  VBoarder Structure Enforcement"
echo "═══════════════════════════════════════════════════════════════"
echo ""

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"

DRY_RUN=${DRY_RUN:-false}

echo "📂 Root directory: $ROOT"
echo "🔍 Dry run: $DRY_RUN"
echo ""

# Function to move files to correct location
enforce_move() {
    local source_pattern="$1"
    local dest_dir="$2"
    local description="$3"

    # Create destination directory
    if [ "$DRY_RUN" = "false" ]; then
        mkdir -p "$dest_dir"
    fi

    local files=()
    while IFS= read -r -d '' file; do
        # Skip if already in correct location
        if [[ "$file" == ./"$dest_dir"/* ]]; then
            continue
        fi
        files+=("$file")
    done < <(find . -maxdepth 1 -name "$source_pattern" -type f -print0 2>/dev/null || true)

    if [ ${#files[@]} -eq 0 ]; then
        return
    fi

    echo ""
    echo "📋 $description → $dest_dir/"
    for file in "${files[@]}"; do
        basename_file=$(basename "$file")
        echo "   • $basename_file"

        if [ "$DRY_RUN" = "false" ]; then
            mv "$file" "$dest_dir/"
        fi
    done

    echo "   ✅ Moved ${#files[@]} file(s)"
}

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Organizing Files by Type"
echo "═══════════════════════════════════════════════════════════════"

# Move stray operation scripts to tools/ops/
enforce_move "repair-*.sh" "tools/ops" "Repair scripts"
enforce_move "fix-*.sh" "tools/ops" "Fix scripts"
enforce_move "rebuild-*.sh" "tools/ops" "Rebuild scripts"
enforce_move "validate-*.sh" "tools/ops" "Validation scripts"
enforce_move "test-*.sh" "tools/ops" "Test scripts"
enforce_move "check-*.sh" "tools/ops" "Check scripts"
enforce_move "update-*.sh" "tools/ops" "Update scripts"

# Move Python operation scripts
enforce_move "rebuild-*.py" "tools/ops" "Rebuild Python scripts"
enforce_move "fix-*.py" "tools/ops" "Fix Python scripts"
enforce_move "update-*.py" "tools/ops" "Update Python scripts"

# Move documentation to docs/
enforce_move "TROUBLESHOOTING.md" "docs" "Troubleshooting guide"
enforce_move "*_GUIDE.md" "docs" "Guide documents"
enforce_move "*_NOTES.md" "docs" "Note documents"
enforce_move "ARCHITECTURE*.md" "docs" "Architecture docs"

# Move test/beta documentation
enforce_move "BETA_TEST*.md" "docs" "Beta test docs"
enforce_move "*_PLAYBOOK.md" "docs" "Playbooks"

# Move verification scripts to tools/ops/
enforce_move "verify_*.sh" "tools/ops" "Verification scripts"
enforce_move "diagnose-*.sh" "tools/ops" "Diagnostic scripts"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Enforcement Summary"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ "$DRY_RUN" = "false" ]; then
    echo "✅ Structure enforcement complete!"
    echo ""
    echo "📁 Key directories organized:"
    echo "   • tools/ops/ - Operation scripts"
    echo "   • docs/ - Documentation files"
    echo ""
    echo "🎯 Root is now clean and organized"
else
    echo "🔍 DRY RUN COMPLETE"
    echo ""
    echo "To execute enforcement, run:"
    echo "  bash tools/cleanup/enforce-root-structure.sh"
fi

echo ""
