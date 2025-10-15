from fastapi import APIRouter, Query

from api.memory_manager import load_agent_context

router = APIRouter()


@router.get("/context")
async def get_agent_context(
    agent: str = Query(..., description="Agent ID (e.g. CTO, CEO)"),
    max_facts: int = Query(5, ge=1, le=50),
    max_messages: int = Query(5, ge=1, le=50),
):
    context = await load_agent_context(
        agent=agent, max_facts=max_facts, max_messages=max_messages
    )
    return context
