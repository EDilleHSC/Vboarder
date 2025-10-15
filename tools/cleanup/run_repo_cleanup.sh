#!/usr/bin/env bash
# VBoarder Repository Cleanup Script (WSL/Linux/macOS)
# Removes build caches, extra venvs, logs, and temporary files
# Safe to run repeatedly - only removes regenerable artifacts

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.."; pwd)"

echo "═══════════════════════════════════════════════"
echo "  VBoarder Repository Cleanup (Safe Mode)"
echo "═══════════════════════════════════════════════"
echo ""

# Helper function
safe_rm() {
    local target="$1"
    if [ -e "$target" ] || [ -L "$target" ]; then
        echo "  → Removing: $target"
        rm -rf "$target"
    fi
}

# 1) Remove extra virtualenvs (keep .venv-wsl only)
echo "[1/7] Removing duplicate virtual environments..."
safe_rm "$ROOT/venv"
safe_rm "$ROOT/api/venv"
safe_rm "$ROOT/agents/venv"
echo "  ✓ Complete"
echo ""

# 2) Remove Node build caches
echo "[2/7] Removing Node.js build caches..."
safe_rm "$ROOT/vboarder_frontend/.next"
safe_rm "$ROOT/vboarder_frontend/nextjs_space/.next"
safe_rm "$ROOT/vboarder_frontend/nextjs_space/.nextcache"
safe_rm "$ROOT/api/ui/node_modules"
safe_rm "$ROOT/api/ui/dist"
echo "  ✓ Complete"
echo ""

# 3) Remove Python caches
echo "[3/7] Removing Python caches..."
find "$ROOT" -type d -name "__pycache__" -print0 2>/dev/null | xargs -0 rm -rf || true
find "$ROOT" -type d -name ".pytest_cache" -print0 2>/dev/null | xargs -0 rm -rf || true
find "$ROOT" -type d -name ".mypy_cache" -print0 2>/dev/null | xargs -0 rm -rf || true
find "$ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$ROOT" -type f -name "*.pyo" -delete 2>/dev/null || true
echo "  ✓ Complete"
echo ""

# 4) Remove logs (regenerated at runtime)
echo "[4/7] Removing log files..."
safe_rm "$ROOT/logs"
find "$ROOT/agents" -maxdepth 2 -type d -name "logs" -print0 2>/dev/null | xargs -0 rm -rf || true
safe_rm "$ROOT/api/ollama.log"
echo "  ✓ Complete"
echo ""

# 5) Trim heavy agent data (keep config/code)
echo "[5/7] Trimming agent memory files..."
find "$ROOT/agents" -maxdepth 2 -type f \( -name "memory.json" -o -name "memory.jsonl" \) -delete 2>/dev/null || true
find "$ROOT/agents" -type d -name "backups" -print0 2>/dev/null | xargs -0 rm -rf || true
echo "  ✓ Complete"
echo ""

# 6) Remove duplicate registries (keep root only)
echo "[6/7] Removing duplicate agent registries..."
safe_rm "$ROOT/api/agent_registry.json"
safe_rm "$ROOT/agents/agent_registry.json"
safe_rm "$ROOT/agents/SEC/agent_registry.json"
safe_rm "$ROOT/agents/CTO/agent_registry.json"
safe_rm "$ROOT/agents/tools/agent_registry.json"
echo "  ✓ Complete"
echo ""

# 7) Delete junk files
echo "[7/7] Removing junk files..."
safe_rm "$ROOT/New Text Document.txt"
safe_rm "$ROOT/To"
safe_rm "$ROOT/wsl"
echo "  ✓ Complete"
echo ""

echo "═══════════════════════════════════════════════"
echo "  Cleanup Complete!"
echo "═══════════════════════════════════════════════"
echo ""
echo "Removed:"
echo "  • Duplicate virtual environments"
echo "  • Build caches (Node.js, Python)"
echo "  • Log files"
echo "  • Agent memory files (regenerable)"
echo "  • Duplicate registries"
echo "  • Temporary/junk files"
echo ""
echo "Next steps:"
echo "  1. Verify tests still pass: pytest -q"
echo "  2. Reinstall frontend if needed: cd vboarder_frontend/nextjs_space && npm ci"
echo "  3. Check disk space saved: du -sh ."
echo ""
