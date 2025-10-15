# Changelog

All notable changes to VBoarder will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0-beta.1] - 2025-10-14

### Added

- **Core Backend API**:

  - `/health` endpoint for basic health checks
  - `/ready` endpoint for comprehensive K8s/LB readiness probes (registry, memory, agent dirs)
  - `/agents` endpoint returning all available agents from registry
  - `/chat/{agent_role}` endpoint for synchronous chat
  - `/chat_stream/{agent_role}` async streaming endpoint (prepared for SSE)
  - `/api/memory` endpoint for memory persistence (accepts string or dict)
  - CORS middleware restricted to localhost origins

- **Development Tools**:

  - **Dev Dashboard** (`devdash.py`) - One-click web GUI to start/stop backend/frontend
    - Browser-based control panel at http://127.0.0.1:4545
    - Start/stop/restart buttons for both services
    - Live log viewing (last 200/120 lines)
    - Quick links to all endpoints
    - Process management with PID tracking
    - No terminal juggling required!

- **Agent System**:

  - 9 executive agents (CEO, CTO, CFO, COO, CMO, CLO, COS, SEC, AIR)
  - Per-agent memory with JSONL persistence
  - Global memory cache with async file operations
  - Agent registry with role validation
  - Flexible persona and prompt loading

- **Testing Infrastructure**:

  - 25 comprehensive tests covering health, agents, chat, memory, streaming
  - 100% test pass rate (4.03s execution)
  - Integration tests for memory persistence

- **Frontend (Next.js)**:

  - ChatGPT-like dark theme interface
  - Markdown rendering support (ReactMarkdown + remark-gfm)
  - Thread management with sidebar
  - Agent avatars and typing indicators
  - Environment configuration (.env.example)

- **Documentation**:

  - Comprehensive deployment guides
  - API endpoint documentation
  - Frontend dependencies guide
  - Production polish roadmap (P0/P1/P2 features)
  - Quick start guides for backend and full stack
  - Repository structure guide (`REPO_STRUCTURE.md`) documenting canonical vs legacy paths

- **Cleanup Tools**:
  - `scripts/run_repo_cleanup.sh` (WSL/Linux/macOS)
  - `scripts/run_repo_cleanup.ps1` (Windows PowerShell)
  - Idempotent scripts to safely remove build artifacts, caches, and duplicates

### Changed

- **Repository Consolidation**:
  - Unified agent registry to root-level `agent_registry.json` (single source of truth)
  - Updated all `api/main.py` references to use root registry (3 locations)
  - Removed duplicate registries from `api/`, `agents/`, and agent subdirectories
  - Standardized to single virtual environment (`.venv-wsl`)
  - Removed duplicate venvs (`venv/`, `api/venv/`, `agents/venv/`)
- Upgraded `.gitignore` with comprehensive Python/Node/OS patterns
- Fixed agent registry parser to use `isinstance()` checks
- Made `MemoryUpdatePayload` flexible (accepts string or dict)
- Improved error handling in memory operations

### Fixed

- Agent registry parsing errors with mixed types
- Test import issues (test_health.py)
- Memory payload validation errors (422 responses)
- CORS configuration for development workflow
- Async/await consistency in connector methods

### Security

- Environment variable templates for safe configuration
- CORS restricted to localhost origins
- API key infrastructure prepared (requires X-API-Key header)

## [Unreleased]

### Planned for v0.9.0-beta.2

- SSE streaming for ChatGPT-like UX
- Message actions (copy, edit, regenerate, delete)
- Enhanced error UX with toast notifications
- Persistent thread storage
- Agent profile cards with example prompts
- Request telemetry UI (tokens, latency)
- Structured JSON logging

### Planned for v1.0.0

- Authentication system (JWT/OAuth)
- Rate limiting per user/IP
- SQLite adapter for better concurrency
- Prometheus metrics endpoint
- Feature flags system
- Full accessibility (WCAG 2.1 AA)
- Theme system (dark/light/high-contrast)

---

[0.9.0-beta.1]: https://github.com/yourusername/vboarder/releases/tag/v0.9.0-beta.1
