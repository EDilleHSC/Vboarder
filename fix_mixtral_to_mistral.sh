#!/bin/bash
# Fix all mixtral references to mistral in VBoarder codebase
# Usage: bash fix_mixtral_to_mistral.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔍 Auditing VBoarder for 'mixtral' references..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backup directory
BACKUP_DIR=".mixtral_fix_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "💾 Backup directory: $BACKUP_DIR"
echo ""

# Files to exclude
EXCLUDE_DIRS=(
    "node_modules"
    ".git"
    ".venv"
    ".venv-wsl"
    "__pycache__"
    ".next"
    "dist"
    "build"
)

# Build exclude pattern for grep
EXCLUDE_PATTERN=""
for dir in "${EXCLUDE_DIRS[@]}"; do
    EXCLUDE_PATTERN="$EXCLUDE_PATTERN --exclude-dir=$dir"
done

# Find all files with "mixtral" (case-insensitive)
echo "🔎 Searching for 'mixtral' references..."
MIXTRAL_FILES=$(grep -ril "mixtral" . $EXCLUDE_PATTERN \
    --exclude="*.md" \
    --exclude="fix_mixtral_to_mistral.sh" \
    --exclude="*.log" \
    --exclude="*.bak" \
    2>/dev/null || true)

if [ -z "$MIXTRAL_FILES" ]; then
    echo "${GREEN}✅ No 'mixtral' references found in code files!${NC}"
    echo ""
    echo "📋 Checking documentation files..."
    DOC_FILES=$(grep -ril "mixtral" . $EXCLUDE_PATTERN \
        --include="*.md" \
        2>/dev/null || true)

    if [ -n "$DOC_FILES" ]; then
        echo "${YELLOW}📄 Found in documentation (informational only):${NC}"
        echo "$DOC_FILES"
    fi

    exit 0
fi

echo "${YELLOW}⚠️  Found 'mixtral' in the following files:${NC}"
echo "$MIXTRAL_FILES"
echo ""

# Count files
FILE_COUNT=$(echo "$MIXTRAL_FILES" | wc -l)
echo "📊 Total files with 'mixtral': $FILE_COUNT"
echo ""

# Ask for confirmation
read -p "❓ Create backups and replace 'mixtral' with 'mistral'? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted. No changes made."
    exit 1
fi

echo ""
echo "🔧 Processing files..."
echo ""

FIXED_COUNT=0
ERROR_COUNT=0

while IFS= read -r file; do
    if [ -n "$file" ]; then
        echo "  📝 Processing: $file"

        # Create backup
        backup_path="$BACKUP_DIR/$(dirname "$file")"
        mkdir -p "$backup_path"
        cp "$file" "$BACKUP_DIR/$file"

        # Count occurrences before
        BEFORE_COUNT=$(grep -oi "mixtral" "$file" | wc -l)

        # Replace mixtral with mistral (preserve case)
        if sed -i 's/mixtral/mistral/gi' "$file" 2>/dev/null; then
            AFTER_COUNT=$(grep -oi "mixtral" "$file" | wc -l || echo "0")
            REPLACED=$((BEFORE_COUNT - AFTER_COUNT))

            if [ $REPLACED -gt 0 ]; then
                echo "     ${GREEN}✅ Replaced $REPLACED occurrence(s)${NC}"
                FIXED_COUNT=$((FIXED_COUNT + 1))
            else
                echo "     ${YELLOW}⚠️  No changes made${NC}"
            fi
        else
            echo "     ${RED}❌ Error processing file${NC}"
            ERROR_COUNT=$((ERROR_COUNT + 1))
        fi
    fi
done <<< "$MIXTRAL_FILES"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Files fixed:  $FIXED_COUNT"
echo "  ❌ Errors:       $ERROR_COUNT"
echo "  💾 Backups:      $BACKUP_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $FIXED_COUNT -gt 0 ]; then
    echo "${GREEN}✅ Successfully replaced 'mixtral' with 'mistral' in $FIXED_COUNT file(s)${NC}"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Review changes:"
    echo "     git diff"
    echo ""
    echo "  2. Test VBoarder:"
    echo "     bash start_vboarder.sh"
    echo ""
    echo "  3. If issues occur, restore from backup:"
    echo "     cp -r $BACKUP_DIR/* ."
    echo ""
else
    echo "${YELLOW}⚠️  No files were modified${NC}"
fi

# Special check for agent config files
echo "🤖 Verifying agent configurations..."
AGENT_CONFIGS=$(find agents/ -name "config.json" 2>/dev/null || true)

if [ -n "$AGENT_CONFIGS" ]; then
    BAD_AGENTS=0
    while IFS= read -r config; do
        if grep -q '"model".*"mixtral"' "$config" 2>/dev/null; then
            echo "  ${RED}❌ Still has mixtral: $config${NC}"
            BAD_AGENTS=$((BAD_AGENTS + 1))
        fi
    done <<< "$AGENT_CONFIGS"

    if [ $BAD_AGENTS -eq 0 ]; then
        echo "  ${GREEN}✅ All agent configs use 'mistral'${NC}"
    else
        echo "  ${RED}⚠️  $BAD_AGENTS agent(s) still reference 'mixtral'${NC}"
        echo "  Run this script again or manually fix the configs."
    fi
else
    echo "  ${YELLOW}ℹ️  No agent config files found${NC}"
fi

echo ""
echo "✅ Done!"
