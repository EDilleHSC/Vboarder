"""
AIR (AI Researcher) Agent Logic
AI research, innovation, and technical exploration.
"""

from agents.agent_base_logic import build_agent_prompt


async def build_air_prompt(user_input: str) -> str:
    """
    Build AIR system prompt with memory context.

    Args:
        user_input: The user's message/request

    Returns:
        Complete system prompt for AIR
    """
    custom_instructions = """
As AI Researcher, your responsibilities include:
- AI/ML research and experimentation
- Evaluating new AI technologies and tools
- Prototyping AI-driven features
- Technical documentation and knowledge sharing
- Best practices for AI implementation
- Staying current with AI research and trends
"""

    return await build_agent_prompt(
        agent_id="AIR",
        user_input=user_input,
        max_facts=15,
        max_messages=10,
        custom_instructions=custom_instructions,
    )
