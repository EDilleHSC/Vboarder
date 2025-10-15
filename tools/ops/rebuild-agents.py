#!/usr/bin/env python3
"""
VBoarder Agent Structure Rebuilder
Rebuilds missing persona.json files and ensures all agents have required structure.
"""
import json
from pathlib import Path
from typing import Dict

# Agent definitions with roles and descriptions
AGENTS = {
    "CEO": {
        "title": "Chief Executive Officer",
        "description": "Strategic leadership and executive decision-making for VBoarder",
        "model": "mixtral:latest",
    },
    "CTO": {
        "title": "Chief Technology Officer",
        "description": "Technical architecture and technology strategy for VBoarder",
        "model": "codellama:latest",
    },
    "CFO": {
        "title": "Chief Financial Officer",
        "description": "Financial planning and fiscal management for VBoarder",
        "model": "mixtral:latest",
    },
    "COO": {
        "title": "Chief Operating Officer",
        "description": "Operations management and process optimization for VBoarder",
        "model": "mixtral:latest",
    },
    "CMO": {
        "title": "Chief Marketing Officer",
        "description": "Marketing strategy and brand development for VBoarder",
        "model": "mixtral:latest",
    },
    "CLO": {
        "title": "Chief Legal Officer",
        "description": "Legal compliance and risk management for VBoarder",
        "model": "mixtral:latest",
    },
    "COS": {
        "title": "Chief of Staff",
        "description": "Coordination and strategic execution for VBoarder",
        "model": "mixtral:latest",
    },
    "SEC": {
        "title": "Security Officer",
        "description": "Security operations and threat management for VBoarder",
        "model": "mixtral:latest",
    },
    "AIR": {
        "title": "AI Research Lead",
        "description": "AI research and innovation for VBoarder",
        "model": "mixtral:latest",
    },
}


def create_persona_json(role: str, agent_info: Dict) -> Dict:
    """Create persona.json structure."""
    return {
        "role": role,
        "title": agent_info["title"],
        "description": agent_info["description"],
        "version": "1.0.0",
        "model": agent_info.get("model", "mixtral:latest"),
    }


def create_config_json(role: str, agent_info: Dict) -> Dict:
    """Create config.json structure."""
    return {
        "role": role,
        "model": agent_info.get("model", "mixtral:latest"),
        "temperature": 0.7,
        "max_tokens": 2000,
        "persona_file": f"agents/{role}/personas/system_detailed.txt",
        "memory_file": f"agents/{role}/memory.jsonl",
    }


def create_system_prompt(role: str, agent_info: Dict) -> str:
    """Create basic system prompt."""
    return f"""You are the {agent_info['title']} for VBoarder.

Role: {role}
Responsibility: {agent_info['description']}

Your responses should be:
- Professional and concise
- Aligned with your role's expertise
- Focused on actionable insights
- Strategic and well-reasoned

Always maintain the perspective and expertise of a {agent_info['title']}.
"""


def rebuild_agents():
    """Rebuild all agent structures."""
    base_dir = Path("agents")
    base_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("VBoarder Agent Structure Rebuilder")
    print("=" * 70)
    print()

    created = 0
    updated = 0

    for role, info in AGENTS.items():
        agent_dir = base_dir / role
        agent_dir.mkdir(exist_ok=True)

        print(f"Processing {role}...")

        # Create personas directory
        personas_dir = agent_dir / "personas"
        personas_dir.mkdir(exist_ok=True)

        # Create/update persona.json
        persona_file = agent_dir / "persona.json"
        persona_data = create_persona_json(role, info)
        if not persona_file.exists():
            with open(persona_file, "w", encoding="utf-8") as f:
                json.dump(persona_data, f, indent=2, ensure_ascii=False)
            print("  ✅ Created persona.json")
            created += 1
        else:
            print("  ℹ️  persona.json exists")

        # Create/update config.json
        config_file = agent_dir / "config.json"
        config_data = create_config_json(role, info)
        if not config_file.exists():
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print("  ✅ Created config.json")
            created += 1
        else:
            print("  ℹ️  config.json exists")

        # Create system_detailed.txt in personas/
        system_prompt_file = personas_dir / "system_detailed.txt"
        if not system_prompt_file.exists():
            system_prompt_file.write_text(
                create_system_prompt(role, info), encoding="utf-8"
            )
            print("  ✅ Created personas/system_detailed.txt")
            created += 1
        else:
            print("  ℹ️  personas/system_detailed.txt exists")

        print()

    print("=" * 70)
    print("✅ Rebuild complete!")
    print(f"   Created: {created} files")
    print("   Existing: Files not overwritten")
    print()
    print("Next steps:")
    print("  1. Verify: bash tools/ops/verify-agent-setup.sh")
    print("  2. Fix registry: python3 tools/ops/fix-registry-paths.py")
    print("  3. Restart backend")
    print("=" * 70)


if __name__ == "__main__":
    rebuild_agents()
