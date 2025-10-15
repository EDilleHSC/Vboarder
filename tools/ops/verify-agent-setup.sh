#!/usr/bin/env bash
# Agent Setup Verification Script
# Ensures all agents have required files and proper configuration

set -euo pipefail

echo "═══════════════════════════════════════════════"
echo "  VBoarder Agent Setup Verification"
echo "═══════════════════════════════════════════════"
echo ""

AGENTS_DIR="agents"
REQUIRED_FILES=("config.json" "personas/system_detailed.txt")
ISSUES=0

# Read agent list from registry
if [ ! -f "agent_registry.json" ]; then
    echo "❌ agent_registry.json not found!"
    exit 1
fi

# Extract agent roles (handle both list and dict formats)
ROLES=$(python3 -c "
import json
with open('agent_registry.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
if isinstance(data, list):
    roles = [a['role'] for a in data]
else:
    roles = [a['role'] for a in data.get('agents', [])]
print(' '.join(roles))
")

echo "Found agents: $ROLES"
echo ""

# Check each agent
for role in $ROLES; do
    agent_dir="$AGENTS_DIR/$role"

    if [ ! -d "$agent_dir" ]; then
        echo "❌ Missing directory: $agent_dir"
        ISSUES=$((ISSUES + 1))
        continue
    fi

    echo "Checking $role..."

    # Check required files
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$agent_dir/$file" ]; then
            echo "  ⚠️  Missing: $file"
            ISSUES=$((ISSUES + 1))
        else
            echo "  ✅ Found: $file"
        fi
    done

    echo ""
done

echo "═══════════════════════════════════════════════"
if [ $ISSUES -eq 0 ]; then
    echo "✅ All agents configured correctly!"
else
    echo "⚠️  Found $ISSUES issue(s)"
    echo ""
    echo "To fix missing agent folders, run:"
    echo "  cp -r agents/CEO agents/MISSING_ROLE"
    echo "  # Then edit personas and config files"
fi
echo "═══════════════════════════════════════════════"
