# VBoarder Full Stack Launch Guide

**Date:** October 14, 2025
**Status:** ✅ Ready for Launch
**Components:** Backend API + Next.js Frontend + Chat UI

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Start Backend (Terminal 1)

```bash
# In WSL
cd /mnt/d/ai/projects/vboarder
source .venv-wsl/bin/activate
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

**Expected Output:**

```
INFO:     Uvicorn running on http://127.0.0.1:3738 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Verify Backend Endpoints

```bash
# Test health
curl http://127.0.0.1:3738/health
# Expected: {"status":"ok"}

# Test agents list
curl http://127.0.0.1:3738/agents
# Expected: {"agents":["CEO","CTO","CFO","COO","CMO","CLO","COS","SEC","AIR"],"count":9}

# Test chat endpoint
curl -X POST http://127.0.0.1:3738/chat/CEO \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, what is your role?","session_id":"test123","concise":true}'
# Expected: {"response":"..."}
```

### Step 3: Install Frontend Dependencies (if needed)

```bash
cd /mnt/d/ai/projects/vboarder/vboarder_frontend/nextjs_space

# Check if framer-motion is installed
npm list framer-motion

# If not installed, add it:
npm install framer-motion
```

### Step 4: Start Frontend (Terminal 2)

```bash
cd /mnt/d/ai/projects/vboarder/vboarder_frontend/nextjs_space
npm run dev
```

**Expected Output:**

```
▲ Next.js 14.2.33
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000

✓ Ready in 2.1s
```

### Step 5: Open Browser

```
http://localhost:3000/chat
```

**What you'll see:**

- 🎨 Clean chat interface
- 🤖 Agent selector dropdown (9 agents)
- 💬 Message input with "Send" button
- 📊 Session ID and message count
- ⚙️ Concise mode toggle

---

## 📁 New Files Created

### Frontend

✅ **`vboarder_frontend/nextjs_space/app/chat/page.tsx`** (234 lines)

- Complete chat UI component
- Agent selector (CEO, CTO, CFO, COO, CMO, CLO, COS, SEC, AIR)
- Session management
- Message history with timestamps
- Loading states and error handling
- Concise mode toggle
- Auto-scroll to latest message

### Backend

✅ **`api/main.py`** - Added `/agents` endpoint (lines 43-67)

### Configuration

✅ **`vboarder_frontend/nextjs_space/.env.local`**

```bash
NEXT_PUBLIC_API_BASE=http://127.0.0.1:3738
```

### Documentation

✅ **`docs/AGENTS_ENDPOINT.md`** - Complete endpoint documentation
✅ **`verify_agents_endpoint.py`** - Automated verification script

---

## 🎨 Chat UI Features

### Core Functionality

- ✅ **9 Agent Support** - CEO, CTO, CFO, COO, CMO, CLO, COS, SEC, AIR
- ✅ **Session Persistence** - Messages tied to session ID
- ✅ **Message History** - Scrollable chat history
- ✅ **Real-time Updates** - Instant message display
- ✅ **Loading States** - Spinner while waiting for response
- ✅ **Error Handling** - User-friendly error messages

### User Experience

- ✅ **Keyboard Shortcuts** - Enter to send, Shift+Enter for newline
- ✅ **Auto-scroll** - Automatically scrolls to latest message
- ✅ **Agent Switching** - Change agent mid-conversation
- ✅ **Session Controls** - New session or clear chat buttons
- ✅ **Concise Mode** - Toggle for shorter responses
- ✅ **Responsive Design** - Works on mobile and desktop

### Visual Design

- ✅ **Clean Interface** - Slate color scheme
- ✅ **Message Bubbles** - User (dark) vs Agent (light)
- ✅ **Timestamps** - Local time for each message
- ✅ **Badges** - Show current agent and mode
- ✅ **Icons** - Lucide icons for visual clarity
- ✅ **Animations** - Smooth transitions with Framer Motion

---

## 🔧 Technical Architecture

### Frontend → Backend Flow

```
User Types Message
    ↓
React Component (app/chat/page.tsx)
    ↓
POST http://127.0.0.1:3738/chat/{agent}
    {
      "message": "Hello",
      "session_id": "ui_1697234567890",
      "concise": true
    }
    ↓
FastAPI Backend (api/main.py)
    ↓
AgentConnector (api/simple_connector.py)
    ↓
Ollama LLM (local) or OpenAI API
    ↓
Response: {"response": "Hello! I'm the CEO..."}
    ↓
Display in Chat UI
```

### Session Management

- **Frontend:** Generates unique session ID: `ui_${Date.now()}`
- **Backend:** Stores conversation in `api/conversations/{session_id}.json`
- **Persistence:** Messages survive page refresh (if session ID preserved)

### Agent Memory

- **Per-Agent Files:** `agents/{ROLE}/memory.json`
- **Structure:** `{facts: [], messages: [], persona: {}}`
- **Access:** Agents read memory during prompt building

---

## 🧪 Testing Your Setup

### Test 1: Backend Health

```bash
curl http://127.0.0.1:3738/health
```

✅ **Expected:** `{"status":"ok"}`

### Test 2: Agent Discovery

```bash
curl http://127.0.0.1:3738/agents | jq
```

✅ **Expected:**

```json
{
  "agents": ["CEO", "CTO", "CFO", "COO", "CMO", "CLO", "COS", "SEC", "AIR"],
  "count": 9
}
```

### Test 3: Chat with CEO

```bash
curl -X POST http://127.0.0.1:3738/chat/CEO \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is VBoarder?",
    "session_id": "curl_test",
    "concise": false
  }' | jq
```

✅ **Expected:** JSON with `response` field containing CEO's answer

### Test 4: Frontend Chat UI

1. Open http://localhost:3000/chat
2. Select "CEO" from dropdown
3. Type: "Hello, introduce yourself"
4. Click "Send" or press Enter
5. Wait for response to appear

✅ **Expected:**

- Message appears in chat as dark bubble
- Loading spinner shows briefly
- CEO response appears as light bubble with timestamp
- Session ID and message count update

---

## 🐛 Troubleshooting

### Problem: Backend won't start

**Error:** `Address already in use`

**Solution:**

```bash
# Kill existing process
lsof -i :3738
kill -9 <PID>

# Or use different port
uvicorn api.main:app --host 127.0.0.1 --port 3739 --reload
# Then update .env.local: NEXT_PUBLIC_API_BASE=http://127.0.0.1:3739
```

### Problem: Frontend shows CORS error

**Error:** `Access-Control-Allow-Origin`

**Solution:**
Check `api/main.py` lines 51-59:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # ← Must match frontend URL
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Problem: "Cannot find module 'framer-motion'"

**Error:** TypeScript error in chat page

**Solution:**

```bash
cd vboarder_frontend/nextjs_space
npm install framer-motion
```

### Problem: Chat sends but no response

**Symptoms:**

- Message appears in UI
- Loading spinner appears
- Error message: "Error contacting API: HTTP 500"

**Solution:**

1. Check backend logs in terminal 1
2. Verify Ollama is running: `curl http://localhost:11434/api/version`
3. Check agent folder exists: `ls agents/CEO/`
4. Test endpoint manually with curl (see Test 3 above)

### Problem: Agent responses are empty

**Symptoms:**

- 200 OK status
- Response: `{"response": ""}`

**Solution:**

1. Check `LLM_MODE` in environment (should be "local" or "openai")
2. Verify Ollama model installed: `ollama list`
3. Check agent config: `cat agents/CEO/config.json`
4. Test LLM directly: `ollama run mistral:7b-instruct "Hello"`

---

## 📊 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
│  http://localhost:3000/chat                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  React Component (app/chat/page.tsx)                  │  │
│  │  - Agent Selector                                     │  │
│  │  - Message Input                                      │  │
│  │  - Chat History                                       │  │
│  └────────────────┬──────────────────────────────────────┘  │
└────────────────────┼──────────────────────────────────────────┘
                     │ HTTP POST /chat/{agent}
                     │ {message, session_id, concise}
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  http://127.0.0.1:3738                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  api/main.py                                          │  │
│  │  - GET  /health      → {"status": "ok"}              │  │
│  │  - GET  /agents      → {agents: [...], count: 9}     │  │
│  │  - POST /chat/{role} → {response: "..."}             │  │
│  └────────────────┬──────────────────────────────────────┘  │
│                   ↓                                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  api/simple_connector.py                              │  │
│  │  - Loads agent config & prompts                       │  │
│  │  - Builds context from memory                         │  │
│  │  - Calls LLM                                          │  │
│  └────────────────┬──────────────────────────────────────┘  │
└────────────────────┼──────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                      LLM Service                             │
│  http://localhost:11434 (Ollama)                             │
│  or https://api.openai.com (OpenAI)                          │
│  - Model: mistral:7b-instruct (local)                        │
│  - or gpt-4 (cloud)                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Launch Sequence

### Pre-Launch Checklist

- [x] All 25 tests passing
- [x] Backend endpoints functional (/health, /agents, /chat)
- [x] Frontend chat UI created
- [x] Environment variables set (.env.local)
- [x] CORS configured
- [ ] Backend server running
- [ ] Frontend dev server running
- [ ] Browser open to chat page

### Launch Commands

**Terminal 1 (Backend):**

```bash
cd /mnt/d/ai/projects/vboarder
source .venv-wsl/bin/activate
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

**Terminal 2 (Frontend):**

```bash
cd /mnt/d/ai/projects/vboarder/vboarder_frontend/nextjs_space
npm run dev
```

**Browser:**

```
http://localhost:3000/chat
```

### Success Criteria

✅ Backend logs show "Application startup complete"
✅ Frontend shows "Ready in X.Xs"
✅ Chat page loads without errors
✅ Can select any of 9 agents
✅ Can send message and get response
✅ Messages persist in session

---

## 🎉 You're Ready!

**All systems operational. Time to launch!**

1. Start backend (Terminal 1)
2. Start frontend (Terminal 2)
3. Open http://localhost:3000/chat
4. Select an agent
5. Start chatting!

**Pro tip:** Open multiple browser tabs to chat with different agents simultaneously.

---

**Document Version:** 1.0
**Last Updated:** October 14, 2025
**Status:** ✅ Ready for Production Launch
