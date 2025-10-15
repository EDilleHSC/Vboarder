#!/bin/bash
# VBoarder Status Dashboard - Quick dopamine hit
# Run with: ./vboarder_status.sh

echo "🎯 VBoarder Development Status"
echo "=================================="

# Check virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Virtual environment: ACTIVE"
else
    echo "⚠️  Virtual environment: NOT ACTIVE"
fi

# Check backend
if curl -s http://127.0.0.1:3738/health >/dev/null 2>&1; then
    echo "✅ Backend server: RUNNING (port 3738)"
else
    echo "❌ Backend server: NOT RUNNING"
fi

# Check git status
BRANCH=$(git branch --show-current 2>/dev/null)
if [ -n "$BRANCH" ]; then
    echo "✅ Git branch: $BRANCH"

    # Check for uncommitted changes
    if git diff --quiet && git diff --staged --quiet; then
        echo "✅ Working directory: CLEAN"
    else
        echo "⚠️  Working directory: HAS CHANGES"
    fi
else
    echo "❌ Git: NOT A REPOSITORY"
fi

# Check Ollama
if ollama list >/dev/null 2>&1; then
    echo "✅ Ollama: RUNNING"
    if ollama list | grep -q mistral; then
        echo "✅ Mistral model: AVAILABLE"
    else
        echo "⚠️  Mistral model: NOT FOUND"
    fi
else
    echo "❌ Ollama: NOT RUNNING"
fi

# Check key files
if [ -f "reasoning_kernel.py" ] && [ -f "router.py" ] && [ -f "scorer_stub.py" ]; then
    echo "✅ Reasoning kernel: FILES PRESENT"
else
    echo "❌ Reasoning kernel: MISSING FILES"
fi

# Test reasoning endpoint
echo ""
echo "🧪 Quick API Test:"
if curl -s -X POST "http://127.0.0.1:3738/ask" \
   -H "Content-Type: application/json" \
   -d '{"task":"System status check","agent_role":"CEO"}' | jq -r '.status' 2>/dev/null | grep -q "success"; then
    echo "✅ Reasoning endpoint: WORKING"
else
    echo "❌ Reasoning endpoint: FAILED"
fi

echo ""
echo "🎯 Next Steps:"
if [ -z "$VIRTUAL_ENV" ]; then
    echo "   → source .venv-wsl/bin/activate"
fi
if ! curl -s http://127.0.0.1:3738/health >/dev/null 2>&1; then
    echo "   → Run task: '⚡ Perfect Dev Setup'"
fi
echo "   → Happy coding! 🚀"
