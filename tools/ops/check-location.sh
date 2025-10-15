#!/usr/bin/env bash
# Quick navigation and environment check
# Run this if you're lost or in the wrong directory

echo "═══════════════════════════════════════════════════════════════"
echo "  VBoarder - Environment Check & Fix"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Show current location
echo "📍 Current directory:"
echo "   $(pwd)"
echo ""

# Check if we're in the right place
if [[ -f "agent_registry.json" ]] && [[ -d "agents" ]] && [[ -d "tools" ]]; then
    echo "✅ You're in the correct directory (project root)"
    echo ""
    echo "📁 Project structure verified:"
    ls -d agents tools docs api 2>/dev/null | sed 's/^/   /'
    echo ""
    echo "🎯 You're ready to run commands!"
    echo ""
    echo "Next steps:"
    echo "  - Run repair: bash tools/ops/repair-all-agents.sh"
    echo "  - Run validation: bash tools/ops/validate-all.sh"
    echo "  - Test agents: bash tools/ops/test-all-agents.sh"
    echo ""
    exit 0
else
    echo "❌ You're NOT in the project root!"
    echo ""

    # Try to find the project root
    if [[ $(pwd) == *"/vboarder_frontend"* ]] || [[ $(pwd) == *"/nextjs_space"* ]]; then
        echo "🔍 Detected: You're in the frontend directory"
        echo ""
        echo "Fix: Run this command to go back to project root:"
        echo "   cd /mnt/d/ai/projects/vboarder"
        echo ""
    elif [[ $(pwd) == *"/vboarder"* ]]; then
        echo "🔍 You're somewhere in the vboarder tree"
        echo ""
        echo "Fix: Run this to go to project root:"
        echo "   cd /mnt/d/ai/projects/vboarder"
        echo ""
    else
        echo "🔍 You're in an unexpected location"
        echo ""
        echo "Fix: Run this to navigate to vboarder:"
        echo "   cd /mnt/d/ai/projects/vboarder"
        echo ""
    fi

    echo "After navigating, verify with:"
    echo "   ls -d agents tools docs"
    echo ""
    echo "You should see: agents/  tools/  docs/"
    echo ""
    exit 1
fi
