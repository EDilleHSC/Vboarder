#!/usr/bin/env python3
"""
VBoarder Agent Registry Rebuilder
Generates agent_registry.json from agent directories
"""

import json
from pathlib import Path

# Agent definitions
AGENTS = {
    "CEO": {
        "title": "Chief Executive Officer",
        "description": "Strategic leadership and executive decision-making for VBoarder",
        "model": "mistral:latest",
        "temperature": 0.7,
    },
    "CTO": {
        "title": "Chief Technology Officer",
        "description": "Technical architecture and technology strategy for VBoarder",
        "model": "mistral:latest",
        "temperature": 0.5,
    },
    "CFO": {
        "title": "Chief Financial Officer",
        "description": "Financial planning and fiscal management for VBoarder",
        "model": "mistral:latest",
        "temperature": 0.7,
    },
    "COO": {
        "title": "Chief Operating Officer",
        "description": "Operations management and process optimization for VBoarder",
        "model": "mistral:latest",
        "temperature": 0.7,
    },
    "CMO": {
        "title": "Chief Marketing Officer",
        "description": "Marketing strategy and brand development for VBoarder",
        "model": "mistral:latest",
        "temperature": 0.8,
    },
    "CLO": {
        "title": "Chief Legal Officer",
        "description": "Legal compliance and risk management for VBoarder",
        "model": "mistral:latest",
        "temperature": 0.6,
    },
    "COS": {
        "title": "Chief of Staff",
        "description": "Coordination and strategic execution for VBoarder",
        "model": "mistral:latest",
        "temperature": 0.7,
    },
    "SEC": {
        "title": "Security Officer",
        "description": "Security operations and threat management for VBoarder",
        "model": "mistral:latest",
        "temperature": 0.5,
    },
    "AIR": {
        "title": "AI Research Lead",
        "description": "AI research and innovation for VBoarder",
        "model": "mistral:latest",
        "temperature": 0.8,
    },
}


def build_registry():
    """Build agent registry from agent directories"""
    print("=" * 70)
    print("VBoarder Agent Registry Rebuilder")
    print("=" * 70)
    print()

    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    registry_path = project_root / "agent_registry.json"
    agents_dir = project_root / "agents"

    print(f"Project root: {project_root}")
    print(f"Agents dir:   {agents_dir}")
    print(f"Registry:     {registry_path}")
    print()

    # Build registry entries
    registry = []

    for role, info in AGENTS.items():
        agent_dir = agents_dir / role

        if not agent_dir.exists():
            print(f"⚠️  Agent directory not found: {role}")
            continue

        # Build paths (use forward slashes for cross-platform compatibility)
        system_prompt_path = f"agents/{role}/personas/system_detailed.txt"
        memory_path = f"agents/{role}/memory.jsonl"
        persona_file_path = f"agents/{role}/persona.json"
        config_file_path = f"agents/{role}/config.json"

        # Create registry entry
        entry = {
            "role": role,
            "title": info["title"],
            "description": info["description"],
            "model": info["model"],
            "temperature": info["temperature"],
            "max_tokens": 2000,
            "system_prompt": system_prompt_path,
            "memory": memory_path,
            "persona_file": persona_file_path,
            "config_file": config_file_path,
            "enabled": True,
        }

        registry.append(entry)
        print(f"✅ Added {role} - {info['title']}")

    print()
    print("=" * 70)
    print(f"Writing registry with {len(registry)} agents...")

    # Write registry (UTF-8 without BOM)
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print("✅ Registry rebuilt successfully!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Verify: cat agent_registry.json | jq")
    print("  2. Check: bash tools/ops/verify-agent-setup.sh")
    print("  3. Restart: uvicorn api.main:app --reload")
    print()


if __name__ == "__main__":
    build_registry()
