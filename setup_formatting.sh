#!/bin/bash
# VBoarder Auto-Formatting Setup Installer
# Run: bash setup_formatting.sh

set -e

echo "🎨 VBoarder Auto-Formatting Setup"
echo "=================================="
echo ""

# Check if ruff is installed
if ! command -v ruff &> /dev/null; then
    echo "📦 Installing Ruff..."
    pip install ruff
else
    echo "✅ Ruff already installed ($(ruff --version))"
fi

echo ""
echo "🔧 Installing VS Code Ruff extension..."
code --install-extension charliermarsh.ruff || echo "⚠️  VS Code extension install failed (may already be installed)"

echo ""
echo "📝 Verifying configuration files..."

# Check pyproject.toml
if grep -q "\[tool.ruff\]" pyproject.toml 2>/dev/null; then
    echo "✅ pyproject.toml configured"
else
    echo "❌ pyproject.toml not configured properly"
    exit 1
fi

# Check .vscode/settings.json
if [ -f ".vscode/settings.json" ]; then
    if grep -q "charliermarsh.ruff" .vscode/settings.json; then
        echo "✅ VS Code settings configured"
    else
        echo "⚠️  VS Code settings may not be fully configured"
    fi
else
    echo "❌ .vscode/settings.json not found"
    exit 1
fi

echo ""
echo "🪝 Installing pre-commit hook (optional)..."
if [ -f ".githooks/pre-commit" ]; then
    mkdir -p .git/hooks
    cp .githooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✅ Pre-commit hook installed"
else
    echo "⚠️  Pre-commit hook file not found (optional)"
fi

echo ""
echo "🧪 Testing Ruff..."

# Create a temporary test file
cat > /tmp/vboarder_ruff_test.py << 'EOF'
import os
import sys
from typing import Dict,List

def test(x,y):
    return x+y
EOF

echo "   Running: ruff format /tmp/vboarder_ruff_test.py"
ruff format /tmp/vboarder_ruff_test.py

echo "   Running: ruff check /tmp/vboarder_ruff_test.py"
ruff check /tmp/vboarder_ruff_test.py || true

rm /tmp/vboarder_ruff_test.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Auto-formatting setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Next steps:"
echo "  1. Reload VS Code: Ctrl+Shift+P → 'Reload Window'"
echo "  2. Test format on save: Edit a .py file and press Ctrl+S"
echo "  3. Read the guide: docs/AUTO_FORMATTING_GUIDE.md"
echo "  4. Quick reference: FORMATTING_QUICK_REF.md"
echo ""
echo "🎯 Manual commands:"
echo "  - Format project: ruff format ."
echo "  - Check issues: ruff check ."
echo "  - Auto-fix: ruff check --fix ."
echo ""
echo "🚀 Happy coding with auto-formatting!"
