"""
CMO (Chief Marketing Officer) Agent Logic
Marketing strategy, branding, and customer engagement.
"""

from agents.agent_base_logic import build_agent_prompt


async def build_cmo_prompt(user_input: str) -> str:
    """
    Build CMO system prompt with memory context.

    Args:
        user_input: The user's message/request

    Returns:
        Complete system prompt for CMO
    """
    custom_instructions = """
As CMO, your responsibilities include:
- Marketing strategy and brand positioning
- Customer acquisition and retention
- Market research and competitive analysis
- Campaign planning and execution
- Digital marketing and social media strategy
- Customer experience and engagement optimization
"""

    return await build_agent_prompt(
        agent_id="CMO",
        user_input=user_input,
        max_facts=12,
        max_messages=10,
        custom_instructions=custom_instructions,
    )
