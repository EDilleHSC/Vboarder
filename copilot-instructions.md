# 🧭 VBoarder Developer & Copilot Instructions

## Overview

# 🤖 VBoarder – Copilot Development Instructions

## 🧠 System Overview

VBoarder is an **AI executive system** built in Python (FastAPI backend) and React/Next.js frontend. It simulates a company leadership team with AI agents representing key roles: `CEO`, `CTO`, `CFO`, `COS`, `COO`, `CLO`, `CMO`, `SEC`, and `AIR`.

Each agent has:

- A `config.json` (settings)
- A `persona.md` (personality profile)
- A `prompt.txt` (custom system prompt)
- A `memory.jsonl` (local memory file)

---

## 🗂️ Agent layout & onboarding (canonical)

Agents are expected to live under the `agents/` folder using the path `agents/<AGENT_NAME>/`.

For each agent folder include these files:

- `config.json` — core behavior settings used by `simple_connector`/agent loaders.
- `persona.md` — short human-readable description of tone, style, and persona.
- `prompt.txt` — operational prompt used to assemble system messages.
- `memory.jsonl` — newline-delimited JSON memory records (create empty file if missing).

How Copilot should add a new agent:

1. Create folder `agents/new_agent/` (lowercase allowed; runtime code normalizes names).
2. Add `config.json`, `persona.md`, `prompt.txt`, and an empty `memory.jsonl`.
3. Do not hardcode agent names; use filesystem iteration when listing agents.
4. Keep `config.json` minimal; larger persona/prompt content belongs in their respective files.

Example minimal `config.json`:

```
{
  "name": "NEW_AGENT",
  "role": "New Role",
  "model": "ollama/ggml-model",
  "version": "1.0"
}
```

Copilot should use the canonical `agents/<AGENT_NAME>/` layout for new work. Existing references to `agents/agents_v2/` were migrated into `agents/` during the refactor.

The system is modular, testable, and built to run locally — no cloud dependencies.

---

## 📁 Project Structure

```plaintext
vboarder/
├── api/                   # FastAPI app entry point
│   └── server.py          # Import this in tests to avoid triggering full agent init
├── agents/                # All agent subfolders (CEO, CTO, etc.)
│   └── AGENT_NAME/        # Each agent has config, persona, prompt, and memory.jsonl
├── coord/                 # Scheduler + agent sync logic
├── data/                  # Shared state + global memory
│   └── shared_state.json
├── frontend/              # React/Next.js frontend
├── tools/                 # Utility scripts (e.g. ct_check.py)
├── tests/                 # Test folder with conftest.py and unit tests
├── copilot-instructions.md # This file
└── README.md
```

---

## 🔧 Development Rules for Copilot

### ✅ DO:

- Use **absolute imports** (e.g., `from api.server import app`) for test stability.
- Assume `agents/` follows the EXAMPLE structure: `config.json`, `persona.md`, `prompt.txt`, `memory.jsonl`.
- Write **lightweight test files** that only import `server.py`, not `main.py`.
- Output JSONL format for memory files (one JSON object per line).
- Use `uvicorn api.server:app --reload` as the dev server command.
- Keep `memory.jsonl` read/writable by default; create it if missing.

### ❌ DO NOT:

- Import Ollama, RAG memory, or `simple_connector` in tests unless explicitly mocked.
- Hardcode agent names — loop over folders in `agents/`.
- Write tests that require internet, Docker, or external APIs.
- Suggest removing `conftest.py` — it's intentional.

---

## 🧪 Testing Guidance

- Use `pytest tests/test_health.py` as the base pattern.
- Test only core endpoints (`/health`, `/chat/{agent}`).
- Avoid triggering heavy agent init during test discovery.
- Use `conftest.py` for:

  - Setting `sys.path`
  - Mocking Ollama or other external deps

---

## 💡 Usage Notes

- Agents sync via `coord/agent_sync.py`, orchestrated by the `COS` agent.
- Memory aggregation (to global memory) is handled by `AIR`.
- Frontend connects to backend at `/api/` (adjust proxy in Next.js if needed).
- All file paths are Linux-style (use uppercase agent folder names!).

---

## 🛠️ Sample Tasks You Can Help With

- Generate a new agent template (`agents/EXAMPLE/`)
- Create a Docker Compose file to start backend + frontend
- Write FastAPI routes for chat or coordination
- Build a unit test for `/chat/CTO` or any other endpoint
- Add logging to `tools/ct_check.py`
- Help create `POLICY_SOP.md` templates for each agent
- Refactor agent init to delay Ollama/RAG loading until runtime

---

## ✅ MVP Completion Criteria (for Copilot Awareness)

Copilot, VBoarder is complete when:

- All agents have config/persona/prompt/memory files
- Backend + frontend run locally
- Memory aggregation works
- Health tests pass in CI
- SOP files are written
- Optional: Docker and CI are integrated

---

## 🗣️ Prompt Suggestions (For Chat-based Copilot)

Try these:

```
@workspace list all agents and their status
@copilot create a new agent folder called 'CSO' based on EXAMPLE
@copilot write a test for /chat/COO that uses server.py
@copilot refactor main.py to lazily import heavy modules
@copilot write a Docker Compose file for backend + frontend
```

---

## 🤐 Final Note

Keep responses short, relevant, and **never assume access to Ollama or external services** unless clearly mocked. Prioritize **local, testable, modular** code that helps human devs move fast.

---

# End of Instructions

Maintain async safety and memory consistency.

Write small, modular helper functions (no monolithic scripts).

Prefer docstrings and comments for new logic.

🧠 Developer Note
This system models human–AI hybrid collaboration:

The CEO (you) and COS (Chief of Staff AI) coordinate the rest.

The CTO, AIR, and department heads maintain system logic, memory, and sync cycles.

coord/scheduler.py orchestrates all agents every 30 seconds for sync.

Keep all code modular, documented, and agent-driven.
Your AI agents are designed to communicate, not compete.

---

Once you save that, Copilot will automatically “understand” your architecture, conventions, and best practices when suggesting completions.

Would you like me to generate **role-specific Copilot hint files** next — e.g., `agents/agents_v2/CTO/POLICY_SOP.md` and `agents/agents_v2/AIR/POLICY_SOP.md` — so each agent has its own behavior guide?
