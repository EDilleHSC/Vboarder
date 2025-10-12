from fastapi import FastAPI, Request, Depends, HTTPException, status
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
import os, json

# -------------------------------------------------------------------
#  Load .env and initialize
# -------------------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("API_KEY", None)
AGENTS_DIR = Path(__file__).resolve().parent / "agents"

app = FastAPI(title="AI Agent API", version="1.0")

# -------------------------------------------------------------------
#  Models
# -------------------------------------------------------------------
class AskPayload(BaseModel):
    agent: str
    query: str

# -------------------------------------------------------------------
#  Security
# -------------------------------------------------------------------
def verify_api_key(request: Request):
    """Check for correct X-API-Key header."""
    key = request.headers.get("x-api-key")
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server missing API_KEY environment variable."
        )
    if key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key."
        )
    return True

# -------------------------------------------------------------------
#  Routes (protected)
# -------------------------------------------------------------------
@app.get("/api/agents", dependencies=[Depends(verify_api_key)])
def list_agents():
    AGENTS_DIR.mkdir(exist_ok=True)
    return sorted([d.name for d in AGENTS_DIR.iterdir() if d.is_dir() and d.name.isupper()])

@app.get("/api/memory/{agent}", dependencies=[Depends(verify_api_key)])
def get_memory(agent: str):
    mem_path = AGENTS_DIR / agent / "memory.jsonl"
    if not mem_path.exists():
        return {"error": f"No memory found for {agent}"}
    with open(mem_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

@app.get("/api/memory/{agent}/summary", dependencies=[Depends(verify_api_key)])
def get_memory_summary(agent: str):
    summary_path = AGENTS_DIR / agent / "memory_summary.md"
    if not summary_path.exists():
        return {"error": f"No summary found for {agent}"}
    return {"summary": summary_path.read_text(encoding="utf-8")}

@app.post("/api/ask", dependencies=[Depends(verify_api_key)])
def ask_agent(payload: AskPayload):
    agent_dir = AGENTS_DIR / payload.agent
    prompt_file = agent_dir / "prompt.md"
    if not prompt_file.exists():
        return {"error": "Agent not found or invalid setup."}
    return {
        "agent": payload.agent,
        "query": payload.query,
        "response": f"🤖 Simulated response from {payload.agent}"
    }

# -------------------------------------------------------------------
#  Open /api/health (no auth)
# -------------------------------------------------------------------
@app.get("/api/health")
def health_report():
    return {"status": "ok", "message": "System healthy."}
