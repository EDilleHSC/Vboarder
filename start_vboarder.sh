#!/usr/bin/env bash
set -e
echo "🚀 Starting VBoarder Environment..."

cd /mnt/d/ai/projects/vboarder
source .venv-wsl/bin/activate

# Make sure ollama is up
if ! pgrep ollama > /dev/null; then
  echo "🧠 Starting Ollama..."
  nohup ollama serve > /dev/null 2>&1 &
  sleep 2
fi

# Kill old backend if running
if lsof -i :3738 > /dev/null 2>&1; then
  echo "🧹 Cleaning up old backend..."
  kill -9 $(lsof -t -i :3738) || true
fi

# Ensure logs directory exists
mkdir -p logs

# Start backend
echo "⚙️  Launching backend..."
nohup uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload > logs/backend.log 2>&1 &
sleep 3

# Start frontend (if directory exists)
if [ -d "vboarder_frontend/nextjs_space" ]; then
  echo "🌐 Launching frontend..."
  cd vboarder_frontend/nextjs_space
  nohup npm run dev -- -p 3001 > ../../logs/frontend.log 2>&1 &
  cd ../..
else
  echo "⚠️  Frontend directory not found, skipping..."
fi

echo ""
echo "✅ VBoarder is live!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Backend:  http://127.0.0.1:3738"
echo "Health:   http://127.0.0.1:3738/health"
echo "Frontend: http://localhost:3001"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Logs:"
echo "  Backend:  tail -f logs/backend.log"
echo "  Frontend: tail -f logs/frontend.log"
echo ""
