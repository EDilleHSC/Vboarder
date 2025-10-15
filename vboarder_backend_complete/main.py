from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from datetime import datetime

app = FastAPI(title="VBoarder Backend API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str
    timestamp: str
    agent_id: str = "user"


class AgentMessage(BaseModel):
    message: str
    agent_id: str


class AgentStatus(BaseModel):
    id: str
    status: str


AGENTS = [
    {
        "id": "sec",
        "name": "Executive Secretary",
        "role": "Coordination & Delegation",
        "status": "active",
        "avatar": "🎯",
    },
    {
        "id": "cmd",
        "name": "Commander",
        "role": "Strategic Planning",
        "status": "active",
        "avatar": "⚔️",
    },
    {
        "id": "res",
        "name": "Researcher",
        "role": "Data Analysis",
        "status": "idle",
        "avatar": "🔬",
    },
    {
        "id": "dev",
        "name": "Developer",
        "role": "Code Generation",
        "status": "idle",
        "avatar": "💻",
    },
    {
        "id": "doc",
        "name": "Documentarian",
        "role": "Documentation",
        "status": "idle",
        "avatar": "📚",
    },
    {
        "id": "qa",
        "name": "QA Specialist",
        "role": "Quality Assurance",
        "status": "idle",
        "avatar": "✓",
    },
    {
        "id": "des",
        "name": "Designer",
        "role": "UI/UX Design",
        "status": "idle",
        "avatar": "🎨",
    },
    {
        "id": "ana",
        "name": "Analyst",
        "role": "Business Analysis",
        "status": "idle",
        "avatar": "📊",
    },
    {
        "id": "pm",
        "name": "Product Manager",
        "role": "Product Strategy",
        "status": "idle",
        "avatar": "🎯",
    },
]

MESSAGES = []


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/agents")
async def get_agents():
    return {"agents": AGENTS}


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    agent = next((a for a in AGENTS if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.post("/api/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status: AgentStatus):
    agent = next((a for a in AGENTS if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent["status"] = status.status
    return {"success": True, "agent": agent}


@app.post("/api/messages")
async def send_message(message: AgentMessage):
    new_message = {
        "role": "user",
        "content": message.message,
        "timestamp": datetime.now().isoformat(),
        "agent_id": message.agent_id,
    }
    MESSAGES.append(new_message)
    response = {
        "role": "assistant",
        "content": f"[{message.agent_id.upper()}]: Acknowledged - {message.message[:50]}...",
        "timestamp": datetime.now().isoformat(),
        "agent_id": message.agent_id,
    }
    MESSAGES.append(response)
    return {"success": True, "response": response}


@app.get("/api/messages")
async def get_messages(agent_id: str = None):
    if agent_id:
        return {"messages": [m for m in MESSAGES if m.get("agent_id") == agent_id]}
    return {"messages": MESSAGES}


@app.get("/api/metrics")
async def get_metrics():
    return {
        "active_agents": len([a for a in AGENTS if a["status"] == "active"]),
        "total_messages": len(MESSAGES),
        "uptime": "2h 34m",
        "success_rate": 0.98,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
