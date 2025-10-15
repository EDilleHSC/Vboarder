"""
CLO (Chief Legal Officer) Agent Logic
Legal counsel, compliance, and risk management.
"""

from agents.agent_base_logic import build_agent_prompt


async def build_clo_prompt(user_input: str) -> str:
    """
    Build CLO system prompt with memory context.

    Args:
        user_input: The user's message/request

    Returns:
        Complete system prompt for CLO
    """
    custom_instructions = """
As CLO, your responsibilities include:
- Legal counsel and risk assessment
- Contract review and negotiation
- Regulatory compliance and governance
- Intellectual property protection
- Dispute resolution and litigation management
- Corporate policy and ethics oversight
"""

    return await build_agent_prompt(
        agent_id="CLO",
        user_input=user_input,
        max_facts=12,
        max_messages=10,
        custom_instructions=custom_instructions,
    )
