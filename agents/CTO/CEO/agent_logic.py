"""
CEO (Chief Executive Officer) Agent Logic
Strategic leadership and vision setting.
"""

from agents.agent_base_logic import build_agent_prompt


async def build_ceo_prompt(user_input: str) -> str:
    """
    Build CEO system prompt with memory context.

    Args:
        user_input: The user's message/request

    Returns:
        Complete system prompt for CEO
    """
    custom_instructions = """
As CEO, your responsibilities include:
- Setting strategic vision and direction
- Making high-level business decisions
- Coordinating with executive team (CFO, CTO, COO, etc.)
- Communicating company mission and values
- Approving major initiatives and resource allocations
"""

    return await build_agent_prompt(
        agent_id="CEO",
        user_input=user_input,
        max_facts=15,
        max_messages=10,
        custom_instructions=custom_instructions,
    )
