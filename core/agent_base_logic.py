"""
Standard agent logic template for executive agents.
Use this as a base for CEO, CFO, COO, CTO, CLO, CMO, SEC, AIR agents.
"""

from typing import Optional

from api.memory_manager import load_agent_context


async def build_agent_prompt(
    agent_id: str,
    user_input: str,
    max_facts: int = 10,
    max_messages: int = 10,
    custom_instructions: Optional[str] = None,
) -> str:
    """
    Build a memory-aware system prompt for any agent.

    Args:
        agent_id: Agent identifier (e.g., "CEO", "CTO", "CFO")
        user_input: The user's message/request
        max_facts: Maximum number of facts to include
        max_messages: Maximum number of recent messages to include
        custom_instructions: Optional additional role-specific instructions

    Returns:
        Complete system prompt string enriched with agent's context
    """
    # Load agent's context (persona, facts, conversation history)
    context = await load_agent_context(
        agent=agent_id, max_facts=max_facts, max_messages=max_messages
    )

    # Build the prompt
    prompt_parts = [
        f"# {context.get('agent', agent_id)} Agent",
        "",
        "## Your Role & Persona",
    ]

    # Handle persona (could be string or dict)
    persona = context.get("persona", {})
    if isinstance(persona, str):
        prompt_parts.append(persona)
    elif isinstance(persona, dict):
        # Extract relevant persona fields
        if persona.get("description"):
            prompt_parts.append(persona["description"])
        elif persona.get("role"):
            prompt_parts.append(f"You are the {persona['role']}")
        else:
            prompt_parts.append(f"You are the {agent_id} of VBoarder.")
    else:
        prompt_parts.append(f"You are the {agent_id} of VBoarder.")

    prompt_parts.append("")

    # Add accumulated facts/knowledge
    if context.get("facts"):
        prompt_parts.extend(
            ["## Your Knowledge & Context", "Key facts you've learned:", ""]
        )
        for fact in context["facts"]:
            prompt_parts.append(f"- {fact}")
        prompt_parts.append("")

    # Add recent conversation history
    if context.get("recent_messages"):
        prompt_parts.extend(["## Recent Conversation History", ""])
        for msg in context["recent_messages"]:
            sender = msg.get("sender", "unknown")
            content = msg.get("message", msg.get("content", ""))
            timestamp = msg.get("timestamp", "")
            prompt_parts.append(f"**{sender}** ({timestamp}): {content}")
        prompt_parts.append("")

    # Add conversation history summary if available
    if context.get("conversation_history"):
        history = context["conversation_history"]
        if history.get("summary"):
            prompt_parts.extend(["## Session Summary", history["summary"], ""])

    # Add custom role-specific instructions
    if custom_instructions:
        prompt_parts.extend(["## Special Instructions", custom_instructions, ""])

    # Add the current user input
    prompt_parts.extend(
        [
            "## Current Request",
            f"User: {user_input}",
            "",
            f"Respond as {agent_id}, using your accumulated context and expertise:",
        ]
    )

    return "\n".join(prompt_parts)
