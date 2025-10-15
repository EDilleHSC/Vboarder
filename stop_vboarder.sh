#!/usr/bin/env bash
echo "🛑 Stopping VBoarder Environment..."

# Stop backend on port 3738
if lsof -i :3738 > /dev/null 2>&1; then
  echo "🧹 Stopping backend (port 3738)..."
  kill -9 $(lsof -t -i :3738) || true
else
  echo "ℹ️  Backend not running on port 3738"
fi

# Stop frontend on port 3001
if lsof -i :3001 > /dev/null 2>&1; then
  echo "🧹 Stopping frontend (port 3001)..."
  kill -9 $(lsof -t -i :3001) || true
else
  echo "ℹ️  Frontend not running on port 3001"
fi

# Optionally stop Ollama (commented out by default)
# if pgrep ollama > /dev/null; then
#   echo "🧠 Stopping Ollama..."
#   pkill ollama
# fi

echo "✅ VBoarder stopped"
