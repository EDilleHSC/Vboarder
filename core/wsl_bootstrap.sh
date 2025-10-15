#!/bin/bash
# === WSL Virtual Environment Bootstrapper ===

echo "🧼 Cleaning up old venv (if any)..."
rm -rf .venv

echo "📦 Creating new virtual environment..."
python3 -m venv .venv

echo "✅ Activating virtual environment..."
source .venv/bin/activate

echo "📚 Installing dependencies..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install python-dotenv openai anthropic groq requests
fi

echo ""
echo "🎉 Environment ready!"
echo "To activate next time, run:"
echo "  source .venv/bin/activate"
