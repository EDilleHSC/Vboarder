import asyncio
import json
import sys
import types
from fastapi.testclient import TestClient

# Provide a lightweight fake `simple_connector` module so importing `api.main`
# (which does `from simple_connector import AgentConnector`) succeeds during tests.
fake_mod = types.ModuleType("simple_connector")

class _StubConnector:
    def __init__(self, agent_role, session_id):
        self.agent_role = agent_role
        self.session_id = session_id

    def chat(self, message, concise=False):
        return f"[STUB] {self.agent_role}: {message}"

    async def chat_stream(self, message, concise=False):
        yield "stub-"
        await asyncio.sleep(0)
        yield "done"

fake_mod.AgentConnector = _StubConnector
sys.modules["simple_connector"] = fake_mod

# Provide a lightweight fake `shared_memory` module used by api.main
fake_shared = types.ModuleType("shared_memory")
def _fake_shared_block_text(max_items=20):
    return ""
def _fake_maybe_extract_fact(text):
    return None
def _fake_append_fact(fact, source_agent=None):
    return None
fake_shared.shared_block_text = _fake_shared_block_text
fake_shared.maybe_extract_fact = _fake_maybe_extract_fact
fake_shared.append_fact = _fake_append_fact
sys.modules["shared_memory"] = fake_shared

import api.main as api_main


def test_chat_endpoint_monkeypatch(monkeypatch):
    """Mock AgentConnector.chat to avoid real LLM calls and test /chat/{role}."""

    class DummyConnector:
        def __init__(self, agent_role, session_id):
            self.agent_role = agent_role
            self.session_id = session_id

        def chat(self, message, concise=False):
            return f"Echo({self.agent_role}): {message[:50]}"

        async def chat_stream(self, message, concise=False):
            # Async generator that yields two chunks
            yield "chunk1-"
            await asyncio.sleep(0)
            yield "chunk2"

    # Patch AgentConnector in the api.main module
    monkeypatch.setattr(api_main, "AgentConnector", DummyConnector)

    client = TestClient(api_main.app)

    # Ensure the role exists in agent registry fallback (lowercased)
    role = "cto"
    monkeypatch.setattr(api_main, "get_valid_roles", lambda: [role])

    # POST /chat/{role}
    resp = client.post(f"/chat/{role}", json={"message": "Hello", "session_id": "t1"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["agent"] == role.upper()
    assert "response" in body
    assert body["response"].startswith("Echo")


def test_chat_stream_endpoint_monkeypatch(monkeypatch):
    """Mock AgentConnector.chat_stream to test the streaming endpoint."""

    class DummyConnector2:
        def __init__(self, agent_role, session_id):
            self.agent_role = agent_role
            self.session_id = session_id

        async def chat_stream(self, message, concise=False):
            yield "hello"
            await asyncio.sleep(0)
            yield " world"

    monkeypatch.setattr(api_main, "AgentConnector", DummyConnector2)

    client = TestClient(api_main.app)
    role = "cto"
    monkeypatch.setattr(api_main, "get_valid_roles", lambda: [role])

    resp = client.post(f"/chat_stream/{role}", json={"message": "Hi", "session_id": "s1"})
    assert resp.status_code == 200
    content = b""
    for chunk in resp.iter_lines():
        if chunk:
            try:
                obj = json.loads(chunk)
            except Exception:
                continue
            # collect token chunks when present
            if obj.get("token"):
                content += obj["token"].encode('utf-8')

    assert content.decode('utf-8').startswith("hello")
