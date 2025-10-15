"""
CTO (Chief Technology Officer) Agent Logic
Technology strategy, architecture, and engineering leadership.
"""

from agents.agent_base_logic import build_agent_prompt


async def build_prompt(user_input: str) -> str:
    """
    Build CTO system prompt with memory context.
    Kept as build_prompt for backward compatibility.

    Args:
        user_input: The user's message/request

    Returns:
        Complete system prompt for CTO
    """
    return await build_cto_prompt(user_input)


async def build_cto_prompt(user_input: str) -> str:
    """
    Build CTO system prompt with memory context.

    Args:
        user_input: The user's message/request

    Returns:
        Complete system prompt for CTO
    """
    custom_instructions = """
As CTO, your responsibilities include:
- Technology strategy and technical vision
- System architecture and infrastructure decisions
- Engineering team leadership and mentorship
- Technical feasibility assessment
- Security, scalability, and performance optimization
- Evaluating and adopting new technologies
- Technical debt management and code quality standards
"""

    return await build_agent_prompt(
        agent_id="CTO",
        user_input=user_input,
        max_facts=15,
        max_messages=10,
        custom_instructions=custom_instructions,
    )
