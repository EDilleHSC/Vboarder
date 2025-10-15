#!/usr/bin/env bash
# Diagnostic Script - Verify Repair Environment
# Run this to check if all repair prerequisites are met

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  VBoarder Repair Environment Diagnostic"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Determine project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "📍 Detected Paths:"
echo "   Script Dir:   $SCRIPT_DIR"
echo "   Project Root: $PROJECT_ROOT"
echo ""

# Check if we're in the right directory
if [[ ! -f "$PROJECT_ROOT/agent_registry.json" ]]; then
    echo "❌ ERROR: agent_registry.json not found in $PROJECT_ROOT"
    echo "   Make sure you're running from the correct directory"
    exit 1
fi
echo "✅ Project root detected correctly"
echo ""

# Check required repair tools
echo "🔧 Checking Repair Tools:"
TOOLS=(
    "tools/ops/rebuild-agents.py"
    "tools/ops/fix-registry-bom.py"
    "tools/ops/fix-registry-paths.py"
    "tools/ops/repair-all-agents.sh"
    "tools/ops/verify-agent-setup.sh"
)

ALL_FOUND=true
for tool in "${TOOLS[@]}"; do
    if [[ -f "$PROJECT_ROOT/$tool" ]]; then
        echo "   ✅ $tool"
    else
        echo "   ❌ MISSING: $tool"
        ALL_FOUND=false
    fi
done
echo ""

if [[ "$ALL_FOUND" != "true" ]]; then
    echo "❌ Some repair tools are missing!"
    exit 1
fi

# Check Python availability
echo "🐍 Checking Python:"
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "   ✅ Python found: $PYTHON_VERSION"
else
    echo "   ❌ python3 not found in PATH"
    exit 1
fi
echo ""

# Check virtual environment
echo "🔹 Checking Virtual Environment:"
if [[ -d "$PROJECT_ROOT/.venv-wsl" ]]; then
    echo "   ✅ .venv-wsl directory exists"

    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        echo "   ✅ Virtual environment is activated: $VIRTUAL_ENV"
    else
        echo "   ⚠️  Virtual environment NOT activated"
        echo "   Run: source .venv-wsl/bin/activate"
    fi
else
    echo "   ⚠️  .venv-wsl not found at $PROJECT_ROOT/.venv-wsl"
fi
echo ""

# Check agent directories
echo "👥 Checking Agent Directories:"
AGENTS=("CEO" "CTO" "CFO" "COO" "CMO" "CLO" "COS" "SEC" "AIR")
MISSING_COUNT=0
for agent in "${AGENTS[@]}"; do
    if [[ -d "$PROJECT_ROOT/agents/$agent" ]]; then
        echo "   ✅ agents/$agent"
    else
        echo "   ❌ MISSING: agents/$agent"
        ((MISSING_COUNT++))
    fi
done

if [[ $MISSING_COUNT -gt 0 ]]; then
    echo ""
    echo "   ⚠️  $MISSING_COUNT agent directories missing"
fi
echo ""

# Check registry file
echo "📄 Checking Registry:"
if [[ -f "$PROJECT_ROOT/agent_registry.json" ]]; then
    # Check for BOM
    if head -c 3 "$PROJECT_ROOT/agent_registry.json" | grep -q $'\xef\xbb\xbf'; then
        echo "   ⚠️  UTF-8 BOM detected (will be fixed by repair)"
    else
        echo "   ✅ No BOM detected"
    fi

    # Check if valid JSON
    if command -v jq >/dev/null 2>&1; then
        if jq empty "$PROJECT_ROOT/agent_registry.json" 2>/dev/null; then
            echo "   ✅ Valid JSON structure"
        else
            echo "   ⚠️  JSON parsing errors (will be fixed by repair)"
        fi
    else
        if python3 -m json.tool "$PROJECT_ROOT/agent_registry.json" >/dev/null 2>&1; then
            echo "   ✅ Valid JSON structure"
        else
            echo "   ⚠️  JSON parsing errors (will be fixed by repair)"
        fi
    fi
else
    echo "   ❌ agent_registry.json not found!"
    exit 1
fi
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════════"
echo "  Diagnostic Summary"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [[ "$ALL_FOUND" == "true" ]]; then
    echo "✅ All repair tools are present"
    echo ""
    echo "Ready to run repair!"
    echo ""
    echo "Commands:"
    echo "  1. Activate venv (if not already):"
    echo "     source .venv-wsl/bin/activate"
    echo ""
    echo "  2. Run repair:"
    echo "     bash tools/ops/repair-all-agents.sh"
    echo ""
    exit 0
else
    echo "❌ Missing required tools - repair cannot proceed"
    echo ""
    exit 1
fi
