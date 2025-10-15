#!/bin/bash
# Quick WSL Environment Check for VBoarder
# Run: bash wsl_quick_check.sh

echo "🔍 VBoarder WSL Environment Check"
echo "================================="
echo ""

# Check 1: WSL environment
echo "✓ Checking WSL environment..."
if [ -n "$WSL_DISTRO_NAME" ]; then
    echo "  ✅ Running in WSL: $WSL_DISTRO_NAME"
else
    echo "  ❌ Not running in WSL"
    echo "  → Open WSL terminal: Ctrl+Shift+P → 'WSL: New WSL Window'"
    exit 1
fi

# Check 2: Project directory
echo "✓ Checking project directory..."
if [ -d "/mnt/d/ai/projects/vboarder" ]; then
    echo "  ✅ VBoarder directory found"
    cd /mnt/d/ai/projects/vboarder || exit 1
else
    echo "  ❌ VBoarder directory not found at /mnt/d/ai/projects/vboarder"
    exit 1
fi

# Check 3: Python
echo "✓ Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  ✅ $PYTHON_VERSION"
else
    echo "  ❌ Python3 not installed"
    echo "  → Install: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Check 4: Virtual environment
echo "✓ Checking virtual environment..."
if [ -d ".venv-wsl" ]; then
    echo "  ✅ .venv-wsl exists"
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "  ✅ Virtual environment active: $VIRTUAL_ENV"
    else
        echo "  ⚠️  Virtual environment not active"
        echo "  → Run: source .venv-wsl/bin/activate"
    fi
else
    echo "  ❌ .venv-wsl not found"
    echo "  → Create: python3 -m venv .venv-wsl"
    echo "  → Activate: source .venv-wsl/bin/activate"
    echo "  → Install: pip install -r requirements.txt"
    exit 1
fi

# Check 5: Ollama
echo "✓ Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "  ✅ Ollama installed"

    # Check if Ollama is running
    if pgrep -x "ollama" > /dev/null; then
        echo "  ✅ Ollama service running"
    else
        echo "  ⚠️  Ollama not running"
        echo "  → Start: ollama serve &"
    fi

    # Check models
    echo "  📦 Installed models:"
    if ollama list | grep -q "mistral"; then
        echo "    ✅ mistral"
    else
        echo "    ❌ mistral (required)"
        echo "    → Install: ollama pull mistral"
    fi

    if ollama list | grep -q "llama3"; then
        echo "    ✅ llama3"
    else
        echo "    ⚠️  llama3 (recommended)"
        echo "    → Install: ollama pull llama3"
    fi
else
    echo "  ❌ Ollama not installed"
    echo "  → Install: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

# Check 6: Backend service
echo "✓ Checking backend service..."
if curl -s http://127.0.0.1:3738/health > /dev/null 2>&1; then
    echo "  ✅ Backend running on port 3738"
else
    echo "  ❌ Backend not running"
    echo "  → Start: bash start_vboarder.sh"
fi

# Check 7: Required files
echo "✓ Checking required files..."
REQUIRED_FILES=(
    "start_vboarder.sh"
    "stop_vboarder.sh"
    "requirements.txt"
    "api/main.py"
    "agent_registry.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file missing"
    fi
done

echo ""
echo "================================="
echo "✅ Environment check complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Make sure virtual environment is active: source .venv-wsl/bin/activate"
echo "  2. Install dependencies if needed: pip install -r requirements.txt"
echo "  3. Pull Ollama models if needed: ollama pull mistral"
echo "  4. Start VBoarder: bash start_vboarder.sh"
echo "  5. Test health: curl http://127.0.0.1:3738/health"
