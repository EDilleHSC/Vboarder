"""
CFO (Chief Financial Officer) Agent Logic
Financial strategy, budgeting, and analysis.
"""

from agents.agent_base_logic import build_agent_prompt


async def build_cfo_prompt(user_input: str) -> str:
    """
    Build CFO system prompt with memory context.

    Args:
        user_input: The user's message/request

    Returns:
        Complete system prompt for CFO
    """
    custom_instructions = """
As CFO, your responsibilities include:
- Financial planning and budgeting
- Cost analysis and optimization
- Revenue forecasting and reporting
- Investment decisions and capital allocation
- Risk management and compliance
- Presenting financial metrics and KPIs
"""

    return await build_agent_prompt(
        agent_id="CFO",
        user_input=user_input,
        max_facts=12,
        max_messages=10,
        custom_instructions=custom_instructions,
    )
