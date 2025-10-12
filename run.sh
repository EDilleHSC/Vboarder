#!/bin/bash
# === VBoarder Auto-Startup Script ===

PROJECT_DIR="/mnt/d/ai/projects/vboarder"
VENV_DIR="$PROJECT_DIR/.venv"

cd "$PROJECT_DIR" || exit 1

# 1️⃣ Create virtual environment if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "🧩 Creating new virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# 2️⃣ Activate venv
source "$VENV_DIR/bin/activate"

# 3️⃣ Ensure dependencies installed
REQUIRED_PACKAGES=(
    fastapi
    uvicorn
    numpy
    sentence-transformers
    python-dotenv
    requests
    scikit-learn
    torch
    transformers
)

echo "📦 Checking dependencies..."
pip install -q --upgrade pip
pip install -q "${REQUIRED_PACKAGES[@]}"

# 4️⃣ Start the FastAPI server
echo "🚀 Starting VBoarder..."
PYTHONPATH=. uvicorn agents.agent_runtime.server:app --reload --host 0.0.0.0 --port 8000
