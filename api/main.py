import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

# Ensure logs directory exists
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging with file handler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "backend.log"),
        logging.StreamHandler(),  # Keep console output too
    ],
)
logger = logging.getLogger("VBoarderAPI")

from api.memory_manager import (
    ConversationAppendPayload,
    MemoryUpdatePayload,
    append_conversation,
    apply_memory_update,
    get_conversation_history,
    get_memory_state,
    reset_memory_section,
)
from api.routes import context as context_route
from api.routes import metrics as metrics_route  # Dev telemetry endpoints
from api.shared_memory import append_fact, maybe_extract_fact

# Assuming these are available in your environment
# NOTE: AgentConnector is assumed to now contain the async generator method `chat_stream`
from api.simple_connector import AgentConnector

# Initialize FastAPI app
app = FastAPI(title="VBoarder API", version="1.0.0")

# ===== CORE ENDPOINTS (Register IMMEDIATELY after app creation) =====


@app.get("/health")
async def health_check():
    """System health and metrics endpoint."""
    return {"status": "ok"}


@app.get("/ready")
async def readiness_check():
    """Comprehensive readiness check for load balancers and K8s probes."""

    checks = {"registry": False, "memory_access": False, "agent_dirs": False}

    try:
        # Check 1: Agent registry readable (from root)
        root_dir = Path(__file__).parent.parent
        registry_path = root_dir / "agent_registry.json"
        with open(registry_path, "r") as f:
            agents = json.load(f)
            checks["registry"] = (
                len(agents) > 0
                if isinstance(agents, list)
                else len(agents.get("agents", [])) > 0
            )

        # Check 2: Memory folder accessible
        agent_base_dir = root_dir / "agents"
        checks["memory_access"] = agent_base_dir.exists() and os.access(
            agent_base_dir, os.R_OK | os.W_OK
        )

        # Check 3: At least one agent directory exists
        agent_dirs = list(agent_base_dir.glob("*/"))
        checks["agent_dirs"] = (
            len([d for d in agent_dirs if d.is_dir() and not d.name.startswith(".")])
            > 0
        )

        all_ready = all(checks.values())
        status_code = 200 if all_ready else 503

        return JSONResponse(
            status_code=status_code,
            content={
                "ready": all_ready,
                "checks": checks,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
            },
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "ready": False,
                "checks": checks,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@app.get("/agents")
async def list_agents():
    """List all available agent roles from the registry."""
    try:
        # Read from root-level registry
        root_dir = Path(__file__).parent.parent
        registry_path = root_dir / "agent_registry.json"
        with open(registry_path, "r") as f:
            agents = json.load(f)

        # Handle both list and dict formats
        if isinstance(agents, list):
            roles = [a["role"] for a in agents]
        elif isinstance(agents, dict):
            roles = [a["role"] for a in agents.get("agents", [])]
        else:
            roles = []

        return {"agents": roles, "count": len(roles)}
    except Exception as e:
        logger.warning(f"Failed to load agent registry from root: {e}")
        # Fallback to known agents
        fallback = ["CEO", "CFO", "COO", "CTO", "CLO", "CMO", "SEC", "AIR", "COS"]
        return {"agents": fallback, "count": len(fallback)}


# Add CORS middleware (before routers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Add production URLs here when deploying
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (after CORS)
app.include_router(context_route.router, prefix="/api")
# Dev telemetry (optional - comment out in production)
app.include_router(metrics_route.router)

# Configuration
SESSION_ID_PATTERN = re.compile(r"[a-zA-Z0-9_\-]+")
MAX_SESSION_ID_LEN = 100
MAX_TURNS_PER_SESSION = 50

BASE_DIR = Path(__file__).parent
CONV_DIR = BASE_DIR / "conversations"
CONV_DIR.mkdir(exist_ok=True)


# Request model
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    concise: Optional[bool] = False


# ===== Session Manager (Unchanged) =====


def sanitize_session_id(sid: Optional[str]) -> str:
    """Sanitize session ID to prevent filesystem issues."""
    if not sid:
        return "default"
    sid = sid.strip()
    sid = sid[:MAX_SESSION_ID_LEN]
    cleaned = "".join(ch if SESSION_ID_PATTERN.fullmatch(ch) else "-" for ch in sid)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned or "default"


class SessionManager:
    """Centralized class for managing conversation history persistence."""

    def __init__(self, agent_role: str, session_id: str, conv_dir: Path = CONV_DIR):
        self.path = conv_dir / f"{agent_role}_{session_id}.json"

    @staticmethod
    def prune_history(
        messages: List[Dict[str, Any]], max_turns: int = MAX_TURNS_PER_SESSION
    ) -> List[Dict[str, Any]]:
        """Keep only the last max_turns conversational pairs (user+assistant)."""
        if not messages:
            return messages
        user_idxs = [i for i, m in enumerate(messages) if m.get("role") == "user"]
        if len(user_idxs) <= max_turns:
            return messages
        start_idx = user_idxs[-max_turns]
        return messages[start_idx:]

    def read_messages(self) -> List[Dict[str, Any]]:
        """Read conversation history from file."""
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read session file {self.path}: {e}")
            return []

    def write_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Write conversation history to file (after pruning)."""
        pruned_messages = self.prune_history(messages)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.path.open("w", encoding="utf-8") as f:
                json.dump(pruned_messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to write session file {self.path}: {e}")
            raise


# ===== Agent Role Validation Utility =====
def get_valid_roles() -> List[str]:
    """Reads agent roles from root registry, falling back to an empty list on failure."""
    try:
        # Read from root-level registry
        root_dir = Path(__file__).parent.parent
        registry_path = root_dir / "agent_registry.json"
        with open(registry_path, "r") as f:
            agents = json.load(f)
        # FIX: Handle both list and dict formats
        if isinstance(agents, list):
            return [a["role"].lower() for a in agents]
        elif isinstance(agents, dict):
            return [a["role"].lower() for a in agents.get("agents", [])]
        return []
    except Exception as e:
        logger.warning(
            f"Falling back to empty agent roles list due to registry error: {e}"
        )
        return []


# ===== Memory & Conversation Endpoints =====


@app.post("/api/memory")
async def update_memory(payload: MemoryUpdatePayload):
    """Append or update structured agent memory and audit log."""
    try:
        memory_state = await apply_memory_update(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to apply memory update")
        raise HTTPException(status_code=500, detail="Unable to update memory") from exc

    return {
        "status": "ok",
        "agent": payload.agent.upper(),
        "memory": memory_state,
    }


@app.get("/api/memory")
async def fetch_memory(
    agent: str = Query(..., description="Agent identifier, e.g. CTO")
):
    """Retrieve the current structured memory for an agent."""
    memory_state = await get_memory_state(agent)
    return {"agent": agent.upper(), "memory": memory_state}


@app.delete("/api/memory")
async def clear_memory(
    agent: str = Query(..., description="Agent identifier, e.g. CTO"),
    section: Optional[str] = Query(
        None, description="Optional section to reset (persona, facts, messages)"
    ),
):
    """Reset all or part of an agent's structured memory."""
    try:
        memory_state = await reset_memory_section(agent, section)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"agent": agent.upper(), "memory": memory_state}


@app.post("/api/conversation")
async def append_conversation_thread(payload: ConversationAppendPayload):
    """Append conversation messages to an agent's conversation history."""
    try:
        result = await append_conversation(payload)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to append conversation history")
        raise HTTPException(
            status_code=500, detail="Unable to append conversation"
        ) from exc

    return {
        "status": "ok",
        "agent": payload.agent.upper(),
        "session_id": result["session_id"],
        "conversation": result["conversation"],
    }


@app.get("/api/conversation")
async def fetch_conversation(
    agent: str = Query(..., description="Agent identifier, e.g. CTO"),
    session_id: Optional[str] = Query(None, description="Filter to a specific session"),
):
    """Fetch conversation history for an agent or a specific session."""
    try:
        conversation_state = await get_conversation_history(agent, session_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    payload: Dict[str, Any]
    if session_id:
        payload = {
            "agent": agent.upper(),
            "session_id": session_id,
            "conversation": conversation_state,
        }
    else:
        payload = {
            "agent": agent.upper(),
            "conversations": conversation_state.get("conversations", []),
        }
    return payload


# ===== API Endpoints (Modified Sections) =====


@app.get("/")
async def root():
    """Welcome endpoint."""
    # Note: Keeping the static list here for welcoming message simplicity,
    # but actual validation is dynamic/empty fallback.
    return {
        "message": "Welcome to VBoarder API",
        "version": "1.0.0",
        "available_agents": [
            "air",
            "ceo",
            "cfo",
            "clo",
            "cmo",
            "coo",
            "cos",
            "cto",
            "sec",
        ],
        "endpoints": {
            "chat": "/chat/{agent_role}",
            "chat_stream": "/chat_stream/{agent_role}",
            "sessions": "/sessions/{agent_role}",
            "all_sessions": "/sessions",
            "health": "/health",
            "agents": "/agents",
        },
    }


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), agent: str = Query(...), session_id: str = Query(...)
):
    """Upload a file for agent processing."""
    upload_dir = Path("data/uploads") / agent.upper()
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {
        "success": True,
        "filename": file.filename,
        "size": len(content),
        "path": str(file_path),
    }


@app.post("/chat/{agent_role}")
async def chat_with_agent(agent_role: str, request: ChatRequest):
    """Chat with a specific C-suite agent with session management."""
    start_time = time.time()
    valid_roles = get_valid_roles()  # Use dynamic list
    if agent_role.lower() not in valid_roles:
        raise HTTPException(
            status_code=404,
            detail=f"Agent role '{agent_role}' not found or registry failed to load.",
        )

    sid = sanitize_session_id(request.session_id)
    manager = SessionManager(agent_role, sid)

    try:
        history = manager.read_messages()
        user_msg = {"role": "user", "content": request.message}
        history.append(user_msg)
        history_for_llm = manager.prune_history(history)
        connector = AgentConnector(agent_role=agent_role, session_id=sid)

        try:
            _role_val = agent_role.upper()
            fact = maybe_extract_fact(request.message or "")
            if fact:
                append_fact(fact, source_agent=_role_val)
        except Exception as fact_e:
            logger.warning(f"Fact extraction failed: {fact_e}")

        # Chat method is now async and must be awaited
        response = await connector.chat(
            request.message, concise=request.concise or False
        )

        assistant_msg = {"role": "assistant", "content": response}
        history.append(assistant_msg)
        import asyncio

        for i, msg in enumerate(history):
            if asyncio.iscoroutine(msg.get("content")):
                print(f"❌ Coroutine still in history[{i}]:", msg)
        manager.write_messages(history)
        pruned_history = manager.prune_history(history)

        elapsed_time = (time.time() - start_time) * 1000
        turns = len([m for m in pruned_history if m.get("role") == "user"])

        # Structured Logging for non-streaming chat
        logger.info(
            json.dumps(
                {
                    "event": "chat_complete",
                    "agent": agent_role,
                    "session": sid,
                    "elapsed_ms": round(elapsed_time, 2),
                    "turns": turns,
                }
            )
        )

        return {
            "agent": agent_role.upper(),
            "session_id": sid,
            "message": request.message,
            "response": response,
            "timestamp": time.time(),
            "response_time_ms": round(elapsed_time, 2),
            "turns_in_session": turns,
        }

    except Exception:
        logger.exception(f"Unexpected error in chat for {agent_role}/{sid}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred during processing."
        )


# =====================================================
# ?? STREAMING CHAT ENDPOINT (Finalized)
# =====================================================


@app.post("/chat_stream/{agent_role}")
async def chat_stream(agent_role: str, request: ChatRequest):
    """
    Stream live responses from a specific agent with full session management.
    """
    start_time = time.time()

    # --- Agent Validation ---
    valid_roles = get_valid_roles()  # Use dynamic list
    if agent_role.lower() not in valid_roles:
        raise HTTPException(
            status_code=404,
            detail=f"Agent role '{agent_role}' not found or registry failed to load.",
        )

    # --- Session and Message Setup ---
    message = request.message
    concise = request.concise
    sid = sanitize_session_id(request.session_id)
    manager = SessionManager(agent_role, sid)

    # 1. Read existing conversation history
    history = manager.read_messages()

    # 2. Add user message
    user_msg = {"role": "user", "content": message}
    history.append(user_msg)

    # 3. Initialize connector and Shared Knowledge
    connector = AgentConnector(agent_role=agent_role, session_id=sid)

    try:
        _role_val = agent_role.upper()
        fact = maybe_extract_fact(message or "")
        if fact:
            append_fact(fact, source_agent=_role_val)
    except Exception as fact_e:
        logger.warning(f"Fact extraction failed: {fact_e}")

    # --- Streaming Generator ---
    async def generate_stream():
        full_response = ""
        try:
            yield json.dumps(
                {"status": "start", "agent": agent_role, "session_id": sid}
            ) + "\n"

            # 4. Get streamed response (Uses the newly implemented connector.chat_stream)
            try:
                # This is now the primary path, yielding true token chunks
                async for token_chunk in connector.chat_stream(
                    message, concise=concise or False
                ):
                    full_response += token_chunk
                    yield json.dumps({"token": token_chunk}) + "\n"
            except AttributeError:
                # Should not happen if simple_connector.py is updated, but kept for safety.
                error_msg = "Connector streaming method failed or is missing."
                logger.error(error_msg)
                yield json.dumps({"error": error_msg}) + "\n"

            # 5. Add assistant response and Save History
            assistant_msg = {"role": "assistant", "content": full_response}
            history.append(assistant_msg)

            manager.write_messages(history)
            pruned_history = manager.prune_history(history)

            # 6. Calculate metrics and finalize stream
            elapsed_time = (time.time() - start_time) * 1000
            turns = len([m for m in pruned_history if m.get("role") == "user"])

            # IMPLEMENTATION OF ADJUSTMENT 5: Structured Logging
            logger.info(
                json.dumps(
                    {
                        "event": "stream_complete",
                        "agent": agent_role,
                        "session": sid,
                        "elapsed_ms": round(elapsed_time, 2),
                        "turns": turns,
                    }
                )
            )

            yield json.dumps(
                {
                    "status": "done",
                    "response_time_ms": round(elapsed_time, 2),
                    "turns_in_session": turns,
                }
            ) + "\n"

        except Exception:
            logger.exception(
                f"Unexpected error in chat_stream generator for {agent_role}/{sid}"
            )
            yield json.dumps(
                {"error": "An unexpected server error occurred during streaming."}
            ) + "\n"

    # Return the StreamingResponse
    return StreamingResponse(generate_stream(), media_type="text/event-stream")


# Remaining endpoints (@app.get("/sessions/{agent_role}"), @app.get("/sessions"),
# @app.delete("/sessions/{agent_role}/{session_id}"), and @app.get("/agents")) are logically
# sound and only rely on the SessionManager and get_valid_roles where appropriate.

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3737)
