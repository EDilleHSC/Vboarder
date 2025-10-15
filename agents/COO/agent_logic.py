"""
COO (Chief Operating Officer) Agent Logic
Operations management and process optimization.
"""

from agents.agent_base_logic import build_agent_prompt


async def build_coo_prompt(user_input: str) -> str:
    """
    Build COO system prompt with memory context.

    Args:
        user_input: The user's message/request

    Returns:
        Complete system prompt for COO
    """
    custom_instructions = """
As COO, your responsibilities include:
- Daily operations management and execution
- Process optimization and efficiency improvements
- Resource allocation and capacity planning
- Team coordination and workflow management
- Quality assurance and operational excellence
- Implementing strategic initiatives on the ground
"""

    return await build_agent_prompt(
        agent_id="COO",
        user_input=user_input,
        max_facts=12,
        max_messages=10,
        custom_instructions=custom_instructions,
    )
