#!/bin/bash
echo "🚀 Starting full VBoarder stack..."

# Start backend
cd /mnt/d/ai/projects/vboarder
source venv/bin/activate
nohup uvicorn server:app --reload --port 8000 > ~/backend.log 2>&1 &
echo "✅ Backend running at http://127.0.0.1:8000"

# Start frontend
cd /mnt/d/ai/projects/vboarder/vboarder_frontend
nohup npm run dev > ~/frontend.log 2>&1 &
echo "✅ Frontend running at http://localhost:3000"

echo "🌐 Both services are live — ready for agent interface."
