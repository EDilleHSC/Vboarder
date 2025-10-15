#!/usr/bin/env python3
"""
VBoarder Model Router
Dynamic model slot selection based on task characteristics.
"""

import os


def pick_model_slot(
    task_chars: int,
    needs_tools: bool = False,
    complexity: str | None = None,
    agent: str = "",
    task: str = "",
) -> str:
    """
    Select appropriate model slot based on task characteristics.

    Slot strategy:
    - slot:a (small, fast) - Simple queries < 1200 chars, no tools
    - slot:b (LFM2e/Liquid) - Strategic/leadership tasks, specialized reasoning
    - slot:c (large) - Complex tasks, tool use, or long context

    Args:
        task_chars: Length of task description in characters
        needs_tools: Whether task requires external tools/APIs
        complexity: Optional complexity hint ("simple", "moderate", "complex")
        agent: Agent role for agent-aware routing
        task: Full task text for LFM2e detection

    Returns:
        str: Model slot identifier (e.g., "slot:a", "slot:b", "slot:c")
    """
    # Check if this should route to LFM2e (slot:b) first
    if is_liquid_ai_task(task, agent):
        return "slot:b"

    # Override with explicit complexity hint
    if complexity == "simple":
        return "slot:a"
    elif complexity == "complex":
        return "slot:c"

    # Tool use always goes to larger model
    if needs_tools:
        return "slot:c"

    # Length-based routing
    if task_chars < 1200:
        return "slot:a"
    elif task_chars < 8000:
        return "slot:b"
    else:
        return "slot:c"


def resolve_model_name(slot: str) -> str:
    """
    Resolve model slot to actual model name.

    Can be overridden with environment variables:
    - MODEL_SLOT_A: Fast, small model (default: mistral:latest)
    - MODEL_SLOT_B: LFM2e/Liquid model for specialized reasoning
    - MODEL_SLOT_C: Large, complex model (default: mistral:latest)

    Args:
        slot: Model slot identifier

    Returns:
        str: Actual model name for Ollama/API
    """
    slot_mapping = {
        "slot:a": os.getenv("MODEL_SLOT_A", "mistral:latest"),
        "slot:b": os.getenv("MODEL_SLOT_B", "lfm2e:latest"),  # LFM2e default
        "slot:c": os.getenv("MODEL_SLOT_C", "mistral:latest"),
    }

    return slot_mapping.get(slot, "mistral:latest")


def is_liquid_ai_task(task: str, agent: str = "") -> bool:
    """
    Detect if task should route to LFM2e/Liquid AI model (slot:b).

    Routes to slot:b for:
    - Planning and optimization tasks
    - Resource allocation scenarios
    - Strategic decision making
    - Multi-step reasoning chains
    - Agent roles: CEO, CTO, COO (leadership roles)

    Args:
        task: Task description
        agent: Agent role (if available)

    Returns:
        bool: True if should use LFM2e model
    """
    # Agent-based routing - leadership roles get sophisticated model
    leadership_agents = ["CEO", "CTO", "COO", "COS", "CFO"]
    if agent.upper() in leadership_agents:
        return True

    # Task-based routing - strategic/planning tasks
    liquid_keywords = [
        "optimize",
        "strategy",
        "plan",
        "resource",
        "allocation",
        "decision",
        "prioritize",
        "coordinate",
        "schedule",
        "analyze",
        "evaluate",
        "compare",
        "recommend",
        "multi-step",
        "complex",
        "reasoning",
        "logic",
    ]

    task_lower = task.lower()
    keyword_matches = sum(1 for keyword in liquid_keywords if keyword in task_lower)

    # Route to LFM2e if multiple strategic keywords or explicit complexity
    return keyword_matches >= 2 or any(
        phrase in task_lower for phrase in ["multi-step", "step by step", "complex reasoning", "strategic planning"]
    )


def detect_tool_requirements(task: str) -> bool:
    """
    Detect if task requires external tools/APIs.

    Heuristic detection based on keywords.

    Args:
        task: Task description

    Returns:
        bool: True if tools likely needed
    """
    tool_keywords = [
        "search",
        "browse",
        "fetch",
        "download",
        "api",
        "database",
        "query",
        "scrape",
        "call",
        "execute",
        "run",
    ]

    task_lower = task.lower()
    return any(keyword in task_lower for keyword in tool_keywords)


def detect_complexity(task: str) -> str:
    """
    Estimate task complexity from text analysis.

    Args:
        task: Task description

    Returns:
        str: "simple", "moderate", or "complex"
    """
    # Simple heuristics
    word_count = len(task.split())
    question_marks = task.count("?")
    has_multi_part = any(word in task.lower() for word in ["and then", "after that", "next", "finally"])

    if word_count < 20 and question_marks <= 1 and not has_multi_part:
        return "simple"
    elif word_count > 100 or has_multi_part or question_marks > 2:
        return "complex"
    else:
        return "moderate"


def route_task(task: str, agent: str = "") -> dict:
    """
    Complete routing decision for a task.

    Args:
        task: Task description
        agent: Agent role for intelligent routing

    Returns:
        dict with routing decision:
            - slot: Model slot identifier
            - model: Resolved model name
            - complexity: Detected complexity level
            - needs_tools: Whether tools are required
            - uses_lfm2e: Whether routed to LFM2e model
    """
    task_chars = len(task)
    needs_tools = detect_tool_requirements(task)
    complexity = detect_complexity(task)

    slot = pick_model_slot(task_chars, needs_tools, complexity, agent, task)
    model = resolve_model_name(slot)

    return {
        "slot": slot,
        "model": model,
        "complexity": complexity,
        "needs_tools": needs_tools,
        "task_length": task_chars,
        "agent": agent,
        "uses_lfm2e": slot == "slot:b",
    }


if __name__ == "__main__":
    # Test router with enhanced LFM2e routing
    test_cases = [
        ("What is 2+2?", ""),
        ("Schedule weekly ops sync without conflicts and ensure tasks are done before end-of-quarter deadline.", "CEO"),
        ("Search the web for latest AI research papers and summarize findings.", "CTO"),
        ("Optimize our resource allocation strategy for Q4", "COO"),
        ("Simple user question", "AIR"),
    ]

    print("🧪 Testing Enhanced Router with LFM2e Integration:\n")
    for task, agent in test_cases:
        result = route_task(task, agent)
        lfm_indicator = " 🧬" if result["uses_lfm2e"] else ""
        print(f"Task: {task[:50]}{'...' if len(task) > 50 else ''}")
        print(f"Agent: {agent or 'None'}")
        print(f"  → Slot: {result['slot']} ({result['model']}){lfm_indicator}")
        print(f"  → Complexity: {result['complexity']}")
        print(f"  → Needs tools: {result['needs_tools']}")
        print(f"  → Uses LFM2e: {result['uses_lfm2e']}")
        print()
