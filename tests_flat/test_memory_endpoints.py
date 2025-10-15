import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.memory_manager import load_agent_context

client = TestClient(app)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_AGENT = "test_memory_agent"
AGENT_DIR = PROJECT_ROOT / "agents" / TEST_AGENT.upper()


@pytest.fixture(autouse=True)
def _clean_agent_dir():
    if AGENT_DIR.exists():
        shutil.rmtree(AGENT_DIR)
    yield
    if AGENT_DIR.exists():
        shutil.rmtree(AGENT_DIR)


def test_memory_write_and_fetch():
    payload = {
        "agent": TEST_AGENT,
        "section": "messages",
        "entry": {
            "sender": "user",
            "message": "Enable Redis integration.",
            "timestamp": "2025-10-13T21:35:00Z",
        },
    }

    response = client.post("/api/memory", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["agent"] == TEST_AGENT.upper()
    assert body["memory"]["messages"][-1]["message"] == "Enable Redis integration."

    # Verify log file was written
    log_path = AGENT_DIR / "memory.jsonl"
    assert log_path.exists()
    with log_path.open("r", encoding="utf-8") as handle:
        lines = handle.readlines()
    assert len(lines) == 1
    log_entry = json.loads(lines[0])
    assert log_entry["section"] == "messages"

    # Fetch current memory state
    fetch_resp = client.get("/api/memory", params={"agent": TEST_AGENT})
    assert fetch_resp.status_code == 200
    fetch_body = fetch_resp.json()
    assert fetch_body["agent"] == TEST_AGENT.upper()
    assert (
        fetch_body["memory"]["messages"][-1]["message"] == "Enable Redis integration."
    )

    # Clear messages section and ensure it is empty
    clear_resp = client.delete(
        "/api/memory",
        params={"agent": TEST_AGENT, "section": "messages"},
    )
    assert clear_resp.status_code == 200
    cleared_body = clear_resp.json()
    assert cleared_body["memory"]["messages"] == []


def test_conversation_append_and_fetch():
    payload = {
        "agent": TEST_AGENT,
        "session_id": "session-abc",
        "messages": [
            {
                "sender": "user",
                "message": "What's our infra status?",
                "timestamp": "2025-10-13T20:00:00Z",
            },
            {
                "sender": "CTO",
                "message": "10 containers running, all stable.",
            },
        ],
    }

    response = client.post("/api/conversation", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["agent"] == TEST_AGENT.upper()
    assert body["session_id"] == "session-abc"
    assert len(body["conversation"]["messages"]) == 2

    # Verify persistence
    convo_path = AGENT_DIR / "conversation_history.json"
    assert convo_path.exists()
    with convo_path.open("r", encoding="utf-8") as handle:
        convo_state = json.load(handle)
    assert convo_state["conversations"][0]["session_id"] == "session-abc"

    # Fetch specific session
    fetch_resp = client.get(
        "/api/conversation",
        params={"agent": TEST_AGENT, "session_id": "session-abc"},
    )
    assert fetch_resp.status_code == 200
    fetch_body = fetch_resp.json()
    assert fetch_body["session_id"] == "session-abc"
    assert len(fetch_body["conversation"]["messages"]) == 2

    # Fetch all conversations
    all_resp = client.get("/api/conversation", params={"agent": TEST_AGENT})
    assert all_resp.status_code == 200
    all_body = all_resp.json()
    assert len(all_body["conversations"]) == 1


@pytest.mark.asyncio
async def test_load_agent_context_returns_recent_data():
    memory_payload = {
        "agent": TEST_AGENT,
        "section": "facts",
        "entry": {"key": "model_type", "value": "Ollama DeepSeek"},
    }
    client.post("/api/memory", json=memory_payload)

    convo_payload = {
        "agent": TEST_AGENT,
        "messages": [
            {"sender": "user", "message": "Ping"},
            {"sender": "CTO", "message": "Pong"},
        ],
    }
    client.post("/api/conversation", json=convo_payload)

    context = await load_agent_context(TEST_AGENT, max_messages=1, max_facts=1)
    assert context["agent"] == TEST_AGENT.upper()
    assert context["facts"][0]["key"] == "model_type"
    assert context["recent_messages"] == []  # facts update does not add messages
    assert context["conversation_history"][0]["message"] == "Pong"


def test_get_agent_context_endpoint():
    client.post(
        "/api/memory",
        json={
            "agent": TEST_AGENT,
            "section": "facts",
            "entry": {"key": "deployment", "value": "10 containers alive"},
        },
    )
    client.post(
        "/api/conversation",
        json={
            "agent": TEST_AGENT,
            "messages": [{"sender": "user", "message": "Status?"}],
        },
    )

    response = client.get(
        "/api/context",
        params={"agent": TEST_AGENT, "max_facts": 1, "max_messages": 1},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["agent"] == TEST_AGENT.upper()
    assert len(body["facts"]) == 1
    assert len(body["conversation_history"]) == 1
