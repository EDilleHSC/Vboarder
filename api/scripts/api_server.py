"""
VBoarder Unified API Server (v3)
Optimized for multi-agent coordination and nested agent discovery.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys

# ✅ Windows Fix — enable subprocess support for asyncio
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("EventLoopPolicy:", type(asyncio.get_event_loop_policy()).__name__)

from typing import Dict, List, Optional, Set

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

# ----------------------------------------------------------------------------- #
# Configuration
# ----------------------------------------------------------------------------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
load_dotenv()

APP_TITLE = "VBoarder Executive API"
API_PORT = int(os.getenv("API_PORT", 8000))
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", 5173))
RELOAD = os.getenv("RELOAD", "true").lower() == "true"
WORKERS = int(os.getenv("WORKERS", "1"))
QUERY_TIMEOUT = int(os.getenv("QUERY_TIMEOUT_SEC", "45"))

SCRIPT_PATH = os.path.join(BASE_DIR, "query_agent_memory.py")
AGENT_JSON = os.path.join(ROOT_DIR, "webui_agents.json")
AGENT_DIR = os.path.join(ROOT_DIR, "agents")

# ----------------------------------------------------------------------------- #
# Logging
# ----------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("vboarder.api")


# ----------------------------------------------------------------------------- #
# Agent Discovery
# ----------------------------------------------------------------------------- #
def discover_agent_files(agent_dir: str) -> Dict[str, Optional[str]]:
    """Locate key files within an agent directory."""
    system_prompt, memory_file, persona_file = None, None, None

    for candidate in [
        "system.txt",
        "system_prompt.txt",
        "prompts/system.txt",
        "prompts/system_detailed.txt",
    ]:
        p = os.path.join(agent_dir, candidate)
        if os.path.exists(p):
            system_prompt = p
            break

    for candidate in ["memory.json", "memory/memory.json", "state/memory.json"]:
        p = os.path.join(agent_dir, candidate)
        if os.path.exists(p):
            memory_file = p
            break

    persona_path = os.path.join(agent_dir, "personas", "vision.txt")
    if os.path.exists(persona_path):
        persona_file = persona_path

    return {
        "system_prompt": system_prompt,
        "memory": memory_file,
        "persona": persona_file,
    }


def load_agents() -> List[dict]:
    """Load agents from webui_agents.json or discover them automatically."""
    if os.path.exists(AGENT_JSON):
        try:
            with open(AGENT_JSON, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} agents from webui_agents.json")
                return [
                    {**a, "code": a.get("agent_name", a.get("code", "")).lower()}
                    for a in data
                ]
        except Exception as e:
            logger.error(f"Failed to read agent registry ({AGENT_JSON}): {e}")

    agents = []
    if os.path.isdir(AGENT_DIR):
        for name in os.listdir(AGENT_DIR):
            path = os.path.join(AGENT_DIR, name)
            if not os.path.isdir(path):
                continue

            files = discover_agent_files(path)
            agent_data = {
                "code": name.lower(),
                "name": name.upper(),
                "system_prompt": files["system_prompt"],
                "memory": files["memory"],
                "persona": files["persona"],
                "path": path,
                "status": "active" if files["system_prompt"] else "incomplete",
            }
            agents.append(agent_data)
            logger.info(f"Loaded agent {name.upper()} -> {files}")

        logger.info(f"Auto-detected {len(agents)} agents from /agents folder.")
    else:
        logger.warning("No /agents directory found.")
    return agents


AGENTS = load_agents()
VALID_AGENTS: Set[str] = {a["code"] for a in AGENTS if a.get("status") == "active"}

# ----------------------------------------------------------------------------- #
# FastAPI Init
# ----------------------------------------------------------------------------- #
app = FastAPI(title=APP_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{FRONTEND_PORT}",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)


# ----------------------------------------------------------------------------- #
# Models
# ----------------------------------------------------------------------------- #
class ChatRequest(BaseModel):
    message: str = Field(..., description="User input message to the agent.")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty.")
        if len(v) > 8000:
            raise ValueError("Message too long (max 8000 chars).")
        return v


class ChatResponse(BaseModel):
    agent: str
    response: str


# ----------------------------------------------------------------------------- #
# Helpers
# ----------------------------------------------------------------------------- #
def assert_script_exists():
    if not os.path.isfile(SCRIPT_PATH):
        raise HTTPException(status_code=500, detail=f"Missing script: {SCRIPT_PATH}")


def parse_query_output(stdout: str) -> str:
    """Try JSON parsing first; fallback to plain text or delimiter section."""
    s = stdout.strip()
    if not s:
        return s
    try:
        data = json.loads(s)
        if isinstance(data, dict):
            for key in ("response", "answer", "result"):
                if key in data:
                    return str(data[key])
        return json.dumps(data)
    except Exception:
        pass
    delimiter = "=" * 70
    return s.split(delimiter)[-1].strip() if delimiter in s else s


async def run_proc_blocking(cmd, cwd=None, env=None, timeout=None):
    """Run subprocess in a thread to avoid Windows asyncio subprocess issues."""
    logger.info("🔧 Using thread+subprocess.run (Windows-safe mode)")

    def _run():
        return subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=False,  # keep bytes; we'll decode explicitly
            timeout=timeout,
            check=False,
        )

    return await asyncio.to_thread(_run)


async def run_query(agent: str, message: str) -> str:
    """Execute agent query via subprocess with timeout (Windows-safe)."""
    assert_script_exists()
    cmd = [sys.executable, SCRIPT_PATH, agent, message]
    logger.info(
        f"Running agent query: agent={agent}, msg_len={len(message)}, py={sys.executable}"
    )

    try:
        res = await run_proc_blocking(
            cmd,
            cwd=os.path.dirname(SCRIPT_PATH),
            env=os.environ.copy(),
            timeout=QUERY_TIMEOUT,
        )

        out_text = (res.stdout or b"").decode("utf-8", errors="replace")
        err_text = (res.stderr or b"").decode("utf-8", errors="replace")

        if res.returncode != 0:
            logger.error(
                f"Query script failed (code {res.returncode}). stderr:\n{err_text}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Query failed (code {res.returncode}): {err_text}",
            )

        if not out_text.strip():
            logger.error(f"Query script produced no output for agent={agent}")
            raise HTTPException(status_code=500, detail="Query returned empty output.")

        return parse_query_output(out_text)

    except subprocess.TimeoutExpired:
        logger.error(f"Query timeout for agent={agent}")
        raise HTTPException(status_code=504, detail="Query timed out.")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during query for agent={agent}")
        raise HTTPException(
            status_code=500, detail=f"Internal error: {type(e).__name__}: {e}"
        )


# ----------------------------------------------------------------------------- #
# Routes
# ----------------------------------------------------------------------------- #
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "agents_total": len(AGENTS),
        "agents_active": len(VALID_AGENTS),
    }


@app.get("/vboarder/agents")
def list_agents():
    return AGENTS


@app.post("/vboarder/chat/{agent}", response_model=ChatResponse)
async def chat_agent(agent: str, req: ChatRequest):
    code = agent.lower()
    if code not in VALID_AGENTS:
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent}' not found or inactive."
        )
    response_text = await run_query(code, req.message)
    return ChatResponse(agent=code, response=response_text)


@app.post("/debug/echo")
async def echo(req: ChatRequest):
    return {"ok": True, "echo": req.message}


@app.get("/debug/probe")
async def probe_subprocess():
    """Test endpoint to verify subprocess works."""
    try:
        res = await run_proc_blocking(
            [sys.executable, "-c", "print('subprocess_ok')"], timeout=5
        )
        out = (res.stdout or b"").decode("utf-8", errors="replace").strip()
        return {"status": "ok", "stdout": out, "returncode": res.returncode}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


# ----------------------------------------------------------------------------- #
# Entrypoint
# ----------------------------------------------------------------------------- #
if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {APP_TITLE} on port {API_PORT}")
    logger.info(f"SCRIPT_PATH: {SCRIPT_PATH} (exists={os.path.isfile(SCRIPT_PATH)})")
    logger.info(f"Python: {sys.executable}")
    logger.info(f"Active agents: {sorted(VALID_AGENTS)}")

    # On Windows, disable reload to avoid supervisor/worker split breaking asyncio subprocess
    is_win = sys.platform.startswith("win")
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=API_PORT,
        reload=False if is_win else (RELOAD and WORKERS == 1),
        workers=1 if is_win or RELOAD else WORKERS,
        log_level="info",
    )
