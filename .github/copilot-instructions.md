## Quick orientation for AI coding agents

This file gives focused, actionable knowledge to be immediately productive in the VBoarder backend.

1) Big picture
- The backend is a FastAPI app that exposes chat and streaming chat endpoints (see `api/main.py` and `server.py`).
- Agents live under `agents/` (per-agent folders are typically UPPERCASE, e.g. `agents/CEO/`). `api/simple_connector.py` is the agent-to-LLM bridge: it loads `config.json`/`agent.json`, persona files, prompts, and optional knowledge files.
- Long-term memory: two coexisting formats:
  - Global JSONL: `data/memory.jsonl` (loaded into `MEMORY_CACHE` in `server.py`).
  - Legacy per-agent JSONL: `agents/*/memory.jsonl` (used by RAG helpers and `_get_embeddings_cached`).

2) Important files to read first
- `api/main.py` — session management, REST endpoints, streaming generator, and conversation persistence under `api/conversations/`.
- `api/simple_connector.py` — how per-agent prompts, personas, and knowledge files are composed into system messages and how Ollama is invoked.
- `server.py` — async embedding helpers, `_EMBEDDING_CACHE`, global memory preload, and LLM/embedding switching (`LLM_MODE`).
- `agent_registry.json` (root and `api/`) — authoritative list of agent roles and paths; `get_valid_roles()` reads this.

3) Run / debug commands (developer workflow)
- Start infra (Postgres / Qdrant / Flowise) with your AI-stack docker-compose (see `docs/README.md`).
- Start the API (from repo root). Example PowerShell commands:

```powershell
uvicorn api.main:app --port 3738 --reload
```

Quick test call (PowerShell):

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:3738/chat/CEO" -Method POST -Body '{"message":"Hello, what is our priority this week?"}' -ContentType "application/json"
```

- Health endpoint: `GET /health` (added in `server.py`) — use this for quick liveness checks.

4) Environment variables and runtime toggles
- `LLM_MODE` — `local` (default, Ollama) or `openai`; see `server.py` for branching.
- `LOCAL_URL`, `OPENAI_URL`, `API_KEY` — model endpoints and credentials.
- `EMBEDDING_URL`, `EMBEDDING_MODEL` — embedding API used by `async_embed_texts`.
- `MAX_MEMORY_MB`, `TOP_K_DEFAULT` — memory sizing and RAG defaults.

5) Project-specific patterns to follow
- Async vs sync: embedding and model calls are async (use `httpx.AsyncClient`, `asyncio.gather`); legacy memory writes remain synchronous. Preserve async boundaries when changing code.
- Cache semantics: `_EMBEDDING_CACHE` includes `mtime` and `timestamp` — invalidate on file modification or after the cache timeout.
- Memory format compatibility: older RAG files use `q`/`a`; the new global memory uses `query`/`response`. Maintain backward compatibility in parsers (`safe_read_jsonl`, `_get_embeddings_cached`).
- Agent layout: `simple_connector._load_agent_config()` expects agent folders under `agents/` named in uppercase and optional files such as `prompts/system_detailed.txt`, `personas/*.txt`, and `config.json` (or `agent.json` referenced from the registry).

6) Integration points and external dependencies
- Ollama (via `ollama`) is used in `api/simple_connector.py` for chat calls; behavior and options vary per agent (see role-specific options in that file).
- RAG connectors: `rag_memory.py` / `init_db_pool()` connect to Postgres + PGVector (ensure DB containers are running before invoking RAG endpoints).
- `shared_memory.py` is used for cross-agent shared facts (see `api/simple_connector.py` and `api/main.py`).

7) Small, safe tasks you can implement
- Health-check unit: test `GET /health` returns JSON `{ "status": "ok" }`.
- Streaming connector: implement `AgentConnector.chat_stream()` as an async generator yielding token chunks; `api/main.py` consumes `async for token_chunk in connector.chat_stream(...)`.

8) Testing and where to be careful
- After changes to embeddings or memory parsing, exercise `/chat/{agent_role}` and `/chat_stream/{agent_role}` and inspect `data/conversations/*` and `data/memory.jsonl` for expected persistence.
- When changing memory writers/readers, update both `safe_read_jsonl()` and `append_jsonl_safe()` to avoid silent data corruption.

If you want, I can expand this with:
- a minimal `agents/EXAMPLE/` template (config + persona + prompt),
- a unit test for `/health`, or
- a short PR checklist showing files to verify when editing LLM/embedding code.

Tell me which of those you want next and I will add it.
## Quick orientation for AI coding agents

This file gives focused, actionable knowledge to be immediately productive in the VBoarder backend.

1) Big picture
- The backend is a FastAPI app that exposes chat and streaming chat endpoints (see `api/main.py` and `server.py`).
- Agents are defined under `agents/` (per-agent folders often UPPERCASE like `agents/CEO/`). `api/simple_connector.py` is the primary bridge that builds system prompts, loads per-agent knowledge, and calls the LLM (Ollama by default).
- Long-term memory: two coexisting systems:
  - New global memory JSONL: `data/memory.jsonl` loaded into `MEMORY_CACHE` in `server.py`.
  - Legacy per-agent JSONL files: `agents/*/memory.jsonl` used by RAG helpers and `_get_embeddings_cached`.

2) Important files to read first
- `api/main.py` — SessionManager, REST endpoints, streaming generator, and how sessions are persisted to `api/conversations/`.
- `api/simple_connector.py` — how agent config, persona, prompts, and knowledge files are loaded and composed into system messages.
- `server.py` — embedding/LLM wrappers, async embedding caching, global memory loading, and config constants (env-driven).
- `agent_registry.json` (root and `api/`) — authoritative list of available roles and paths used by `get_valid_roles()` and tooling.

3) Run / debug commands (developer workflow)
- Start infra (Postgres/Qdrant/Flowise) from the parent AI stack with docker-compose (see `docs/README.md`).
- Start the API (from repo root):
  - PowerShell: `uvicorn api.main:app --port 3738 --reload`
  - Or run `python -m uvicorn api.main:app --port 3738 --reload`
- Health endpoint available at `GET /health` (added in `server.py`) — use this to confirm server liveness.

4) Environment variables and runtime toggles
- `LLM_MODE` — "local" (default / Ollama) or "openai"; see `server.py` for branching logic.
- `LOCAL_URL`, `OPENAI_URL`, `API_KEY` — endpoints/credentials for model calls.
- `EMBEDDING_URL`, `EMBEDDING_MODEL` — embedding service (Ollama or host) used by `async_embed_texts`.
- `MAX_MEMORY_MB`, `TOP_K_DEFAULT` — memory sizing and default RAG settings.

5) Project-specific patterns you must follow
- Async + sync mix: embedding and model calls are async (`httpx.AsyncClient`, `asyncio.gather`), while some I/O (legacy memory writes) is synchronous. When changing embedding/LLM code keep async boundaries intact.
- Cache semantics: `_EMBEDDING_CACHE` in `server.py` includes mtime and timestamp—invalidate on file mtime or timeout.
- Backward-compat keys: older RAG files use `q`/`a`, newer global memory uses `query`/`response`. Keep compatibility in parsers (see `_get_embeddings_cached`, `safe_read_jsonl`).
- Agent folders and config: `simple_connector._load_agent_config()` expects per-agent folders under `agents/` named in uppercase and optional files like `prompts/system_detailed.txt`, `personas/*.txt`, and `config.json` (or `agent.json` per registry).

6) Integration points and external deps
- Ollama (via `ollama` client) is used in `api/simple_connector.py` for chat; fallback and options vary by agent role.
- RAG connectors: `rag_memory.py` / `init_db_pool()` and Postgres + PGVector are referenced — confirm DB containers are running before running endpoints that call RAG.
- `shared_memory.py` is referenced for cross-agent shared facts (see `simple_connector` and `api/main.py`).

7) Minimal examples you can implement safely
- Add a short health-check unit: call `GET /health` and assert JSON `{"status":"ok"}`.
- When adding streaming support, implement `AgentConnector.chat_stream()` as an async generator yielding token chunks; `api/main.py` expects `async for token_chunk in connector.chat_stream(...)`.

8) Testing, changes and where to be careful
- Changing embedding/LLM code: run quick local check by calling `/chat/{agent_role}` and `/chat_stream/{agent_role}` with a short message; inspect `data/conversations/*` files for persisted history.
- When modifying memory formats, update both `safe_read_jsonl()` and any code that writes memory (`append_jsonl_safe`) to avoid silent parsing errors.

If anything here is unclear or you want more examples (prompt templates, common PR patterns, or tests), tell me which section to expand and I will iterate.
