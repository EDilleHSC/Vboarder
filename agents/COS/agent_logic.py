"""
COS (Chief of Staff) Agent Logic
Orchestrator that coordinates across all executive agents.
"""

import asyncio
from typing import Any, Dict, List

from api.memory_manager import load_agent_context


async def build_cos_prompt(
    user_input: str, peer_summaries: List[Dict[str, Any]] = None
) -> str:
    """
    Build COS system prompt with multi-agent coordination context.

    Args:
        user_input: The user's message/request
        peer_summaries: Optional pre-loaded peer agent summaries

    Returns:
        Complete system prompt string for COS
    """
    # 1. Load COS's own context (persona, facts, history)
    cos_context = await load_agent_context("COS", max_facts=10, max_messages=15)

    # 2. Load peer agent summaries for coordination (if not provided)
    if peer_summaries is None:
        peer_ids = ["CEO", "CFO", "COO", "CTO", "CLO", "CMO", "SEC", "AIR"]
        peer_summaries = await load_peer_summaries(peer_ids)

    # 3. Build the orchestration prompt
    prompt_parts = [
        "# CHIEF OF STAFF (COS) - Executive Orchestrator",
        "",
        "## Your Role & Persona",
    ]

    # Handle persona (could be string or dict)
    persona = cos_context.get("persona", {})
    if isinstance(persona, str):
        prompt_parts.append(persona)
    elif isinstance(persona, dict):
        if persona.get("description"):
            prompt_parts.append(persona["description"])
        else:
            prompt_parts.append(
                "You are the Chief of Staff, coordinating executive leadership."
            )
    else:
        prompt_parts.append(
            "You are the Chief of Staff, coordinating executive leadership."
        )

    prompt_parts.extend(["", "## Your Context & Knowledge"])

    # Add COS's own facts
    if cos_context.get("facts"):
        prompt_parts.append("### Key Facts You Know:")
        for fact in cos_context["facts"]:
            prompt_parts.append(f"- {fact}")
        prompt_parts.append("")

    # Add recent conversation context
    if cos_context.get("recent_messages"):
        prompt_parts.append("### Recent Conversation History:")
        for msg in cos_context["recent_messages"]:
            sender = msg.get("sender", "unknown")
            content = msg.get("message", msg.get("content", ""))
            prompt_parts.append(f"- **{sender}**: {content}")
        prompt_parts.append("")

    # 4. Add peer agent summaries for orchestration
    if peer_summaries:
        prompt_parts.extend(
            [
                "## Executive Team Status (Peer Agents)",
                "Coordinate across these agents based on their current context:",
                "",
            ]
        )

        for peer in peer_summaries:
            agent_name = peer.get("agent", "Unknown")
            facts = peer.get("facts", [])
            last_msg = peer.get("last_message")

            prompt_parts.append(f"### {agent_name}")
            if facts:
                prompt_parts.append("Recent focus:")
                for fact in facts[:3]:  # Top 3 facts
                    prompt_parts.append(f"  - {fact}")
            if last_msg:
                content = last_msg.get("message", last_msg.get("content", ""))
                prompt_parts.append(f"Last activity: {content[:100]}...")
            prompt_parts.append("")

    # 5. Add orchestration instructions
    prompt_parts.extend(
        [
            "## Your Orchestration Mission",
            "- Analyze which agents should be involved in the current request",
            "- Coordinate handoffs between specialized agents",
            "- Synthesize insights from multiple executive perspectives",
            "- Maintain coherent cross-functional execution",
            "",
            "## Current Request",
            f"User: {user_input}",
            "",
            "Respond as COS, orchestrating the appropriate executive response:",
        ]
    )

    return "\n".join(prompt_parts)


async def load_peer_summaries(peer_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Load context summaries for all peer agents in parallel.

    Args:
        peer_ids: List of agent IDs to load context for

    Returns:
        List of peer context summaries
    """
    # Load all peer contexts in parallel
    tasks = [
        load_agent_context(peer_id, max_facts=3, max_messages=3) for peer_id in peer_ids
    ]
    contexts = await asyncio.gather(*tasks, return_exceptions=True)

    # Format into summaries
    peer_summaries = []
    for peer_id, ctx in zip(peer_ids, contexts):
        if isinstance(ctx, Exception):
            # Log error but don't fail - continue with other agents
            print(f"[COS] Warning: Could not load context for {peer_id}: {ctx}")
            continue

        peer_summaries.append(
            {
                "agent": ctx.get("agent", peer_id),
                "facts": ctx.get("facts", []),
                "last_message": (
                    ctx.get("recent_messages", [{}])[-1]
                    if ctx.get("recent_messages")
                    else None
                ),
            }
        )

    return peer_summaries


async def cos_chat(user_input: str) -> str:
    """
    Main entry point for COS agent chat with full orchestration context.

    Args:
        user_input: User's message or request

    Returns:
        COS's orchestrated response
    """
    # Build the full orchestration prompt
    system_prompt = await build_cos_prompt(user_input)

    # TODO: Replace with actual LLM call
    # Example: response = await call_llm(system_prompt, user_input)

    return system_prompt  # For now, return the prompt for testing
