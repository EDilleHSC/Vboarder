"""
Integration test for memory-aware agent chat.
Tests the full flow: memory → prompt building → LLM → response.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_AGENT = "CEO"
AGENT_DIR = PROJECT_ROOT / "agents" / TEST_AGENT


@pytest.fixture(autouse=True)
def setup_test_memory():
    """Set up test memory data for CEO."""
    # Ensure agent directory exists
    AGENT_DIR.mkdir(parents=True, exist_ok=True)

    # Create test memory
    memory_data = {
        "facts": [
            "Q3 revenue exceeded targets by 15%",
            "New product launch planned for Q4 2025",
            "Board meeting scheduled for November 1st",
        ],
        "messages": [
            {
                "sender": "user",
                "message": "What's our company focus?",
                "timestamp": "2025-10-13T10:00:00Z",
            },
            {
                "sender": "CEO",
                "message": "Our focus is sustainable growth and innovation.",
                "timestamp": "2025-10-13T10:01:00Z",
            },
        ],
        "context": {"company": "VBoarder", "fiscal_year": 2025},
    }

    memory_file = AGENT_DIR / "memory.json"
    with memory_file.open("w", encoding="utf-8") as f:
        json.dump(memory_data, f, indent=2)

    yield

    # Cleanup (optional - comment out to inspect results)
    # if memory_file.exists():
    #     memory_file.unlink()


@pytest.mark.asyncio
async def test_ceo_chat_with_memory():
    """Test that CEO chat uses memory context."""
    response = client.post(
        f"/chat/{TEST_AGENT}",
        json={
            "message": "What were our Q3 results?",
            "session_id": "integration_test_001",
            "concise": False,
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Response should reference Q3 from memory
    assert "response" in data
    response_text = data["response"].lower()

    # Should mention Q3 or revenue (from memory facts)
    # Note: Actual assertion depends on LLM behavior
    # This is a smoke test to ensure no errors occur
    assert len(response_text) > 0
    print(f"\n[Test] CEO Response: {response_text[:200]}...")


@pytest.mark.asyncio
async def test_cto_chat_without_memory():
    """Test CTO chat when no memory exists (should still work)."""
    response = client.post(
        "/chat/CTO",
        json={
            "message": "What's our tech stack?",
            "session_id": "integration_test_002",
            "concise": False,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "response" in data
    assert len(data["response"]) > 0
    print(f"\n[Test] CTO Response: {data['response'][:200]}...")


@pytest.mark.asyncio
async def test_memory_persists_after_chat():
    """Test that chat interactions update memory files."""
    # First chat
    response1 = client.post(
        f"/chat/{TEST_AGENT}",
        json={
            "message": "Remember: we hired 5 new engineers",
            "session_id": "integration_test_003",
            "concise": False,
        },
    )
    assert response1.status_code == 200

    # Add fact via memory endpoint
    fact_response = client.post(
        "/api/memory",
        json={
            "agent": TEST_AGENT,
            "section": "facts",
            "entry": "Hired 5 new engineers in October 2025",
        },
    )
    assert fact_response.status_code == 200

    # Second chat should have access to the new fact
    response2 = client.post(
        f"/chat/{TEST_AGENT}",
        json={
            "message": "How many engineers did we hire recently?",
            "session_id": "integration_test_003",
            "concise": False,
        },
    )
    assert response2.status_code == 200
    data = response2.json()

    # The response should reference the hiring (from memory)
    # This is a smoke test - actual LLM behavior may vary
    assert len(data["response"]) > 0
    print(f"\n[Test] CEO Response with new fact: {data['response'][:200]}...")


@pytest.mark.asyncio
async def test_context_endpoint_integration():
    """Test that /api/context returns the same data used by chat."""
    # Get context
    context_response = client.get(
        f"/api/context?agent={TEST_AGENT}&max_facts=10&max_messages=10"
    )
    assert context_response.status_code == 200
    context = context_response.json()

    # Verify structure
    assert context["agent"] == TEST_AGENT
    assert "facts" in context
    assert "recent_messages" in context
    assert len(context["facts"]) > 0  # Should have test facts

    print(f"\n[Test] Context facts: {context['facts']}")
    print(f"[Test] Context messages: {len(context['recent_messages'])} messages")


def test_all_agents_accessible():
    """Smoke test: verify all agents can be reached."""
    agents = ["CEO", "CFO", "COO", "CTO", "CLO", "CMO", "SEC", "AIR", "COS"]

    for agent in agents:
        response = client.post(
            f"/chat/{agent}",
            json={
                "message": "Hello, what's your role?",
                "session_id": f"smoke_test_{agent.lower()}",
                "concise": True,
            },
        )

        # Should not error out
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        print(f"\n[Test] {agent} is accessible and responsive")
