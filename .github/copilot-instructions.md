# VBoarder AI Coding Agent Instructions

## Quick orientation for AI coding agents

VBoarder is a multi-agent leadership system with specialized AI agents (CEO, CTO, CFO, etc.) using persistent memory and RAG.

## 1) Architecture Overview

- **FastAPI backend** (`api/main.py`, `server.py`) exposes chat and streaming chat endpoints
- **Agent system**: Each agent lives in `agents/{ROLE}/` (uppercase folders like `agents/CEO/`)
- **Agent connector**: `api/simple_connector.py` loads agent config, personas, prompts, and knowledge files
- **Dual memory system**:
  - Global JSONL: `data/memory.jsonl` (loaded into `MEMORY_CACHE` in `server.py`)
  - Per-agent JSONL: `agents/*/memory.jsonl` (legacy RAG format)

## 2) Key Files to Read First

- `api/main.py` — SessionManager, REST endpoints, conversation persistence (`api/conversations/`)
- `api/simple_connector.py` — agent config loading, system message composition, Ollama calls
- `server.py` — async embedding cache, global memory, LLM/embedding switching
- `agent_registry.json` — authoritative agent roles list (root and `api/` versions)

## 3) Developer Workflow

**Start infrastructure** (from parent AI stack directory):

```bash
docker-compose up -d  # Postgres, Qdrant, Flowise
```

**Start API** (from project root):

```powershell
uvicorn api.main:app --port 3738 --reload
```

**Quick test**:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:3738/chat/CEO" -Method POST -Body '{"message":"Hello, what is our priority this week?"}' -ContentType "application/json"
```

**Health check**: `GET /health` returns `{"status": "ok"}`

## 4) Environment & Configuration

- `LLM_MODE` — "local" (Ollama) or "openai"
- `LOCAL_URL`, `OPENAI_URL`, `API_KEY` — model endpoints/credentials
- `EMBEDDING_URL`, `EMBEDDING_MODEL` — embedding service for RAG
- `MAX_MEMORY_MB`, `TOP_K_DEFAULT` — memory limits and RAG settings

## 5) Critical Project Patterns

- **Async boundaries**: Embedding/LLM calls are async (`httpx.AsyncClient`), legacy I/O is sync
- **Cache invalidation**: `_EMBEDDING_CACHE` uses mtime + timestamp—invalidate on file changes
- **Memory compatibility**: Legacy uses `q`/`a`, new format uses `query`/`response`
- **Agent structure**: Each agent folder expects `config.json`, `personas/*.txt`, `prompts/system_detailed.txt`

## 6) Testing & Validation

- Run existing tests: `pytest Tests/` (includes health check, chat endpoints)
- After memory changes: test `/chat/{role}` and `/chat_stream/{role}`, check `data/conversations/`
- Agent folders follow pattern: `agents/CEO/` with `config.json`, `agent.json`, persona files

## 7) Integration Points

- **Ollama client** in `simple_connector.py` for chat completion
- **Postgres + PGVector** via `rag_memory.py` (ensure DB containers running)
- **Shared facts** via `shared_memory.py` for cross-agent communication

## 8) Safe Starting Tasks

- Add health check tests in `Tests/`
- Implement `AgentConnector.chat_stream()` as async generator
- Add new agent following `agents/EXAMPLE/` pattern
