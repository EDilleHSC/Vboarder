from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
import os
import re
import json
from pathlib import Path
import asyncio
import logging 

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VBoarderAPI")

# Assuming these are available in your environment
# NOTE: AgentConnector is assumed to now contain the async generator method `chat_stream`
from simple_connector import AgentConnector 
from shared_memory import shared_block_text, maybe_extract_fact, append_fact

# Initialize FastAPI app
app = FastAPI(title="VBoarder API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    def prune_history(messages: List[Dict[str, Any]], max_turns: int = MAX_TURNS_PER_SESSION) -> List[Dict[str, Any]]:
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
    """Reads agent roles from registry, falling back to an empty list on failure."""
    try:
        registry_path = os.path.join(os.path.dirname(__file__), "agent_registry.json")
        with open(registry_path, "r") as f:
            agents = json.load(f)
        return [a["role"].lower() for a in agents.get("agents", [])]
    except Exception as e:
        # IMPLEMENTATION OF ADJUSTMENT 2: Replace static fallback with empty list
        logger.warning(f"Falling back to empty agent roles list due to registry error: {e}")
        return []

# ===== API Endpoints (Modified Sections) =====

@app.get("/")
async def root():
    """Welcome endpoint."""
    # Note: Keeping the static list here for welcoming message simplicity, 
    # but actual validation is dynamic/empty fallback.
    return {
        "message": "Welcome to VBoarder API",
        "version": "1.0.0",
        "available_agents": ["air", "ceo", "cfo", "clo", "cmo", "coo", "cos", "cto", "sec"],
        "endpoints": {
            "chat": "/chat/{agent_role}",
            "chat_stream": "/chat_stream/{agent_role}",
            "sessions": "/sessions/{agent_role}",
            "all_sessions": "/sessions",
            "health": "/health",
            "agents": "/agents"
        }
    }

@app.post("/chat/{agent_role}")
async def chat_with_agent(agent_role: str, request: ChatRequest):
    """Chat with a specific C-suite agent with session management."""
    start_time = time.time()
    valid_roles = get_valid_roles() # Use dynamic list
    if agent_role.lower() not in valid_roles:
        raise HTTPException(status_code=404, detail=f"Agent role '{agent_role}' not found or registry failed to load.")
    
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

        response = connector.chat(request.message, concise=request.concise)
        
        assistant_msg = {"role": "assistant", "content": response}
        history.append(assistant_msg)
        manager.write_messages(history)
        pruned_history = manager.prune_history(history)

        elapsed_time = (time.time() - start_time) * 1000
        turns = len([m for m in pruned_history if m.get("role") == "user"])

        # Structured Logging for non-streaming chat
        logger.info(json.dumps({
            "event": "chat_complete",
            "agent": agent_role,
            "session": sid,
            "elapsed_ms": round(elapsed_time, 2),
            "turns": turns
        }))
        
        return {
            "agent": agent_role.upper(),
            "session_id": sid,
            "message": request.message,
            "response": response,
            "timestamp": time.time(),
            "response_time_ms": round(elapsed_time, 2),
            "turns_in_session": turns
        }
        
    except Exception as e:
        logger.exception(f"Unexpected error in chat for {agent_role}/{sid}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during processing.")


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
    valid_roles = get_valid_roles() # Use dynamic list
    if agent_role.lower() not in valid_roles:
        raise HTTPException(status_code=404, detail=f"Agent role '{agent_role}' not found or registry failed to load.")

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
            yield json.dumps({"status": "start", "agent": agent_role, "session_id": sid}) + "\n"
            
            # 4. Get streamed response (Uses the newly implemented connector.chat_stream)
            try:
                # This is now the primary path, yielding true token chunks
                async for token_chunk in connector.chat_stream(message, concise=concise):
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
            logger.info(json.dumps({
                "event": "stream_complete",
                "agent": agent_role,
                "session": sid,
                "elapsed_ms": round(elapsed_time, 2),
                "turns": turns
            }))
            
            yield json.dumps({
                "status": "done",
                "response_time_ms": round(elapsed_time, 2),
                "turns_in_session": turns
            }) + "\n"

        except Exception as e:
            logger.exception(f"Unexpected error in chat_stream generator for {agent_role}/{sid}")
            yield json.dumps({"error": "An unexpected server error occurred during streaming."}) + "\n"

    # Return the StreamingResponse
    return StreamingResponse(generate_stream(), media_type="text/event-stream")


# Remaining endpoints (@app.get("/sessions/{agent_role}"), @app.get("/sessions"), 
# @app.delete("/sessions/{agent_role}/{session_id}"), and @app.get("/agents")) are logically 
# sound and only rely on the SessionManager and get_valid_roles where appropriate.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3737)
