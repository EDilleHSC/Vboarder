"""
Test agent logic integration with memory context loading.
Verifies all agents can build prompts using their context.
"""

from pathlib import Path

import pytest

from agents.AIR.agent_logic import build_air_prompt

# Import all agent logic modules
from agents.CEO.agent_logic import build_ceo_prompt
from agents.CFO.agent_logic import build_cfo_prompt
from agents.CLO.agent_logic import build_clo_prompt
from agents.CMO.agent_logic import build_cmo_prompt
from agents.COO.agent_logic import build_coo_prompt
from agents.COS.agent_logic import build_cos_prompt
from agents.CTO.agent_logic import build_prompt as build_cto_prompt
from agents.SEC.agent_logic import build_sec_prompt

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.asyncio
async def test_ceo_prompt_building():
    """Test CEO can build prompt with memory context."""
    prompt = await build_ceo_prompt("What's our strategic priority this quarter?")
    assert "CEO" in prompt
    assert "strategic" in prompt.lower() or "vision" in prompt.lower()
    assert len(prompt) > 100  # Should have substantial content


@pytest.mark.asyncio
async def test_cfo_prompt_building():
    """Test CFO can build prompt with memory context."""
    prompt = await build_cfo_prompt("What's our budget status?")
    assert "CFO" in prompt
    assert "financial" in prompt.lower() or "budget" in prompt.lower()
    assert len(prompt) > 100


@pytest.mark.asyncio
async def test_coo_prompt_building():
    """Test COO can build prompt with memory context."""
    prompt = await build_coo_prompt("How are operations running?")
    assert "COO" in prompt
    assert "operation" in prompt.lower() or "process" in prompt.lower()
    assert len(prompt) > 100


@pytest.mark.asyncio
async def test_cto_prompt_building():
    """Test CTO can build prompt with memory context."""
    prompt = await build_cto_prompt("What's our tech stack strategy?")
    assert "CTO" in prompt
    assert "tech" in prompt.lower() or "engineer" in prompt.lower()
    assert len(prompt) > 100


@pytest.mark.asyncio
async def test_clo_prompt_building():
    """Test CLO can build prompt with memory context."""
    prompt = await build_clo_prompt("Are we compliant with new regulations?")
    assert "CLO" in prompt
    assert "legal" in prompt.lower() or "compliance" in prompt.lower()
    assert len(prompt) > 100


@pytest.mark.asyncio
async def test_cmo_prompt_building():
    """Test CMO can build prompt with memory context."""
    prompt = await build_cmo_prompt("How's our market positioning?")
    assert "CMO" in prompt
    assert "market" in prompt.lower() or "brand" in prompt.lower()
    assert len(prompt) > 100


@pytest.mark.asyncio
async def test_sec_prompt_building():
    """Test SEC (Secretary) can build prompt with memory context."""
    prompt = await build_sec_prompt("Schedule a board meeting next week.")
    assert "SEC" in prompt
    assert (
        "schedule" in prompt.lower()
        or "calendar" in prompt.lower()
        or "secretary" in prompt.lower()
    )
    assert len(prompt) > 100


@pytest.mark.asyncio
async def test_air_prompt_building():
    """Test AIR can build prompt with memory context."""
    prompt = await build_air_prompt("What AI models should we evaluate?")
    assert "AIR" in prompt
    assert "ai" in prompt.lower() or "research" in prompt.lower()
    assert len(prompt) > 100


@pytest.mark.asyncio
async def test_cos_orchestration_prompt():
    """Test COS can build orchestration prompt with peer context."""
    prompt = await build_cos_prompt(
        "Coordinate a product launch across all departments."
    )
    assert "COS" in prompt or "Chief of Staff" in prompt
    assert "orchestrat" in prompt.lower() or "coordinat" in prompt.lower()
    # COS should have multi-agent context
    assert len(prompt) > 200  # Longer due to peer summaries


@pytest.mark.asyncio
async def test_all_agents_respond_to_same_query():
    """Test all agents can respond to the same query with their unique perspectives."""
    query = "How can we improve our organization?"

    agents = [
        ("CEO", build_ceo_prompt),
        ("CFO", build_cfo_prompt),
        ("COO", build_coo_prompt),
        ("CTO", build_cto_prompt),
        ("CLO", build_clo_prompt),
        ("CMO", build_cmo_prompt),
        ("SEC", build_sec_prompt),
        ("AIR", build_air_prompt),
    ]

    prompts = {}
    for agent_name, build_fn in agents:
        prompt = await build_fn(query)
        prompts[agent_name] = prompt
        assert len(prompt) > 100
        assert agent_name in prompt

    # Verify each agent has unique perspective (prompts should differ)
    unique_prompts = set(prompts.values())
    assert len(unique_prompts) == len(
        agents
    ), "Each agent should have unique prompt content"
