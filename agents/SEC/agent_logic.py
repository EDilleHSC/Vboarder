"""
SEC (Executive Secretary) Agent Logic
Administrative coordination, scheduling, and executive support.
"""

from agents.agent_base_logic import build_agent_prompt


async def build_sec_prompt(user_input: str) -> str:
    """
    Build SEC (Secretary) system prompt with memory context.

    Args:
        user_input: The user's message/request

    Returns:
        Complete system prompt for SEC
    """
    custom_instructions = """
As Executive Secretary, your responsibilities include:
- Executive calendar management and scheduling
- Meeting coordination and agenda preparation
- Communication routing and prioritization
- Document management and record keeping
- Travel arrangements and logistics
- Supporting executive decision-making with information gathering
"""

    return await build_agent_prompt(
        agent_id="SEC",
        user_input=user_input,
        max_facts=15,
        max_messages=12,
        custom_instructions=custom_instructions,
    )
