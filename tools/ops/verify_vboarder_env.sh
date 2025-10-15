#!/usr/bin/env bash
# =========================================================
# 🧠 VBoarder Environment Verification Script
# Version: 1.0.0
# Author: Eric Dille (Automated by GPT-5)
# =========================================================

PROJECT_DIR="/mnt/d/ai/projects/vboarder"
VENV_DIR="$PROJECT_DIR/.venv"
SERVER_URL="http://localhost:8000"

echo "🔍 Verifying VBoarder Environment..."
echo "------------------------------------"

# Check Python version
echo -n "🐍 Python version: "
python3 --version

# Check if virtual environment exists
if [ -d "$VENV_DIR" ]; then
    echo "✅ Virtual environment found: $VENV_DIR"
else
    echo "❌ Virtual environment missing. Run: python3 -m venv .venv"
    exit 1
fi

# Check if venv is active
if [[ "$VIRTUAL_ENV" != "$VENV_DIR" ]]; then
    echo "⚠️  Virtual environment not active. Activating..."
    source "$VENV_DIR/bin/activate"
fi

# Check for key packages
echo "📦 Checking installed packages..."
pip show fastapi httpx numpy psutil > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Missing core packages. Run inside venv:"
    echo "   pip install fastapi uvicorn httpx numpy psutil"
    exit 1
else
    echo "✅ Core Python packages installed."
fi

# Check backend process
echo "🖥️  Checking backend process on port 8000..."
if sudo lsof -i:8000 > /dev/null 2>&1; then
    echo "✅ Backend process detected on port 8000."
else
    echo "❌ No backend running on port 8000."
fi

# Test API endpoints
echo "🌐 Testing API health..."
curl -s "$SERVER_URL/api/health" | jq . > /tmp/vb_health.json 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ API /health check failed."
else
    echo "✅ /api/health reachable."
    jq . /tmp/vb_health.json
fi

echo "📊 Testing system metrics..."
curl -s "$SERVER_URL/api/system/metrics" | jq . > /tmp/vb_metrics.json 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ API /system/metrics check failed."
else
    echo "✅ /api/system/metrics reachable."
    jq . /tmp/vb_metrics.json
fi

echo "------------------------------------"
echo "🧠 Verification complete."
