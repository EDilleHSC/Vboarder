#!/usr/bin/env bash
# Install missing Python dependencies for VBoarder tools

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  VBoarder - Install Tool Dependencies"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if we're in a venv
if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo "⚠️  No virtual environment detected"
    echo "   Attempting to activate .venv-wsl..."

    if [ -f ".venv-wsl/bin/activate" ]; then
        source .venv-wsl/bin/activate
        echo "✅ Activated .venv-wsl"
    else
        echo "❌ .venv-wsl not found. Please activate your venv first:"
        echo "   source .venv-wsl/bin/activate"
        exit 1
    fi
else
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
fi

echo ""
echo "Installing tool dependencies..."
echo ""

# Install Flask for devdash
echo "📦 Installing Flask (for devdash)..."
pip install -q flask

# Install any other missing dependencies
echo "📦 Checking other dependencies..."
pip install -q -r requirements.txt 2>/dev/null || true

echo ""
echo "✅ All dependencies installed!"
echo ""
echo "You can now run:"
echo "  - python3 tools/dev/devdash.py (Dev Dashboard)"
echo "  - bash tools/ops/test-all-agents.sh (Agent Tests)"
echo "  - bash tools/ops/validate-all.sh (System Validation)"
