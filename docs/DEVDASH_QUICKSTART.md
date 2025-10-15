# 🎛️ VBoarder Dev Dashboard - Quick Reference

## One-Command Startup

```bash
python devdash.py
# Open: http://127.0.0.1:4545
```

---

## What You Get

```
┌─────────────────────────────────────────────┐
│  🎛️ Dev Dashboard                           │
│  Control Panel for VBoarder Development     │
├──────────────────┬──────────────────────────┤
│ Backend          │ Frontend                 │
│ FastAPI/Uvicorn  │ Next.js                  │
│                  │                          │
│ Status: Running ✅│ Status: Running ✅       │
│ Port: 3738       │ Port: 3010               │
│                  │                          │
│ [Start] [Stop]   │ [Start] [Stop]           │
│ [Restart]        │ [Restart]                │
│                  │                          │
│ 📜 View Logs     │ 📜 View Logs             │
└──────────────────┴──────────────────────────┘
│ 🔗 Quick Links                              │
│ • Backend Health                            │
│ • Agents List                               │
│ • Frontend UI                               │
│ • API Docs                                  │
└─────────────────────────────────────────────┘
```

---

## Features

✅ **One-Click Start/Stop** - No terminal commands needed
✅ **Live Logs** - View backend/frontend output in browser
✅ **Quick Links** - Access all endpoints from one place
✅ **Process Management** - Automatic PID tracking
✅ **Status Detection** - Real-time service status
✅ **Dark Theme** - Easy on the eyes

---

## Quick Start

### 1. Install Flask (one time)

```bash
pip install flask
```

### 2. Start Dashboard

```bash
cd /mnt/d/ai/projects/vboarder
python devdash.py
```

### 3. Open Browser

```
http://127.0.0.1:4545
```

### 4. Click "Start" Buttons

- Click **Start** on Backend card
- Click **Start** on Frontend card
- Wait 10 seconds for services to boot
- Click frontend link when ready

---

## Environment Variables

```bash
# Backend port (default: 3738)
export VB_BACKEND_PORT=3738

# Frontend port (default: 3010)
export VB_FRONTEND_PORT=3010

# Dashboard port (default: 4545)
export VB_DASH_PORT=4545
```

---

## Files Created

```
d:\ai\projects\vboarder\
├── .devdash_pids.json    ← Process IDs (gitignored)
└── logs/
    ├── backend.log       ← Backend output
    └── frontend.log      ← Frontend output
```

---

## Common Commands

### Start Dashboard

```bash
python devdash.py
```

### Use Custom Ports

```bash
VB_BACKEND_PORT=8000 VB_FRONTEND_PORT=3001 python devdash.py
```

### Use with Make

```bash
make dashboard
```

### Check Status

Open browser, look at Status field:

- ✅ **Green "Running"** = Service is up
- ❌ **Red "Stopped"** = Service is down

---

## Troubleshooting

### Dashboard Won't Start

**Error:** `Address already in use`

```bash
VB_DASH_PORT=4546 python devdash.py
```

### Backend Won't Start

**Error:** `Failed to start backend`

```bash
# Check venv path in devdash.py
ls -la .venv-wsl/bin/uvicorn
```

### Frontend Won't Start

**Error:** `Failed to start frontend`

```bash
cd vboarder_frontend/nextjs_space
npm install
```

### Process Won't Stop

```bash
# Find PID
cat .devdash_pids.json

# Kill manually
kill -9 <PID>

# Clean up
rm .devdash_pids.json
```

---

## Comparison

### Before (Traditional)

```bash
# Terminal 1 - Backend
cd /mnt/d/ai/projects/vboarder
source .venv-wsl/bin/activate
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload

# Terminal 2 - Frontend
cd /mnt/d/ai/projects/vboarder/vboarder_frontend/nextjs_space
npm run dev

# Terminal 3 - Test
curl http://127.0.0.1:3738/health
```

**= 3 terminals, 6+ commands**

### After (Dashboard)

```bash
python devdash.py
# Click "Start" twice
```

**= 1 terminal, 1 command, 2 clicks**

---

## Use Cases

### Daily Development

1. Morning: `python devdash.py` → click Start buttons
2. During day: Code changes auto-reload
3. Check logs: Expand "Logs" section
4. End of day: Click Stop buttons

### Team Onboarding

```bash
# New developer setup:
git clone <repo>
cd vboarder
pip install -r requirements.txt
python devdash.py
# Click Start → you're running!
```

### Debugging

1. Check logs in dashboard
2. Click Restart to reload
3. Click health check link
4. View full logs in browser

### Demos

1. Start dashboard before meeting
2. Click Start buttons
3. Share frontend URL
4. Click Stop after demo

---

## Next Steps

After starting services:

1. **Check Health:** Click "Backend health" link
2. **View Agents:** Click "Agents" link
3. **Open Frontend:** Click "Frontend" link
4. **Test Chat:** Select CEO, send message

---

## Documentation

- **Full Guide:** [docs/DEV_DASHBOARD.md](../docs/DEV_DASHBOARD.md)
- **README:** [README.md](../README.md#-dev-dashboard-easiest-way)
- **Makefile:** `make dashboard`

---

## Tips

### Bookmark These URLs

- Dashboard: http://127.0.0.1:4545
- Backend Health: http://127.0.0.1:3738/health
- Backend Docs: http://127.0.0.1:3738/docs
- Frontend: http://127.0.0.1:3010

### Create Alias

```bash
# Add to .bashrc or .zshrc
alias vb='cd /mnt/d/ai/projects/vboarder && python devdash.py'

# Then just type:
vb
```

### Multiple Projects

```bash
# Project 1
cd /project1 && VB_DASH_PORT=4545 python devdash.py &

# Project 2
cd /project2 && VB_DASH_PORT=4546 python devdash.py &
```

---

**Created:** October 14, 2025
**Status:** ✅ Production Ready
**Questions?** See [docs/DEV_DASHBOARD.md](../docs/DEV_DASHBOARD.md)
