"""
Test script to verify all agent imports work correctly.
Run this before starting the backend to catch import errors early.
"""

import asyncio
import sys


def test_imports():
    """Test that all agent modules can be imported."""
    print("Testing agent imports...")

    try:
        print("  ✓ Importing CEO agent...", end="")
        from agents.CEO.agent_logic import build_ceo_prompt

        print(" OK")

        print("  ✓ Importing CTO agent...", end="")
        from agents.CTO.agent_logic import build_prompt as build_cto_prompt

        print(" OK")

        print("  ✓ Importing CFO agent...", end="")
        from agents.CFO.agent_logic import build_cfo_prompt

        print(" OK")

        print("  ✓ Importing COO agent...", end="")
        from agents.COO.agent_logic import build_coo_prompt

        print(" OK")

        print("  ✓ Importing CMO agent...", end="")
        from agents.CMO.agent_logic import build_cmo_prompt

        print(" OK")

        print("  ✓ Importing CLO agent...", end="")
        from agents.CLO.agent_logic import build_clo_prompt

        print(" OK")

        print("  ✓ Importing COS agent...", end="")
        from agents.COS.agent_logic import build_cos_prompt

        print(" OK")

        print("  ✓ Importing SEC agent...", end="")
        from agents.SEC.agent_logic import build_sec_prompt

        print(" OK")

        print("  ✓ Importing AIR agent...", end="")
        from agents.AIR.agent_logic import build_air_prompt

        print(" OK")

        print("\n✅ All agent imports successful!")
        return True

    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        return False


async def test_prompt_building():
    """Test that prompt builders work."""
    print("\nTesting prompt builders...")

    try:
        from agents.CEO.agent_logic import build_ceo_prompt
        from agents.SEC.agent_logic import build_sec_prompt

        print("  ✓ Testing CEO prompt builder...", end="")
        ceo_prompt = await build_ceo_prompt("Test message", max_facts=5, max_messages=5)
        assert isinstance(ceo_prompt, str)
        assert len(ceo_prompt) > 0
        print(" OK")

        print("  ✓ Testing SEC prompt builder...", end="")
        sec_prompt = await build_sec_prompt("Test message", max_facts=5, max_messages=5)
        assert isinstance(sec_prompt, str)
        assert len(sec_prompt) > 0
        print(" OK")

        print("\n✅ All prompt builders working!")
        return True

    except Exception as e:
        print(f"\n❌ Prompt building failed: {e}")
        return False


def test_api_imports():
    """Test that API modules can be imported."""
    print("\nTesting API imports...")

    try:
        print("  ✓ Importing simple_connector...", end="")
        from api.simple_connector import AgentConnector

        print(" OK")

        print("  ✓ Importing memory_manager...", end="")
        from api.memory_manager import load_agent_context

        print(" OK")

        print("  ✓ Importing main app...", end="")
        from api.main import app

        print(" OK")

        print("\n✅ All API imports successful!")
        return True

    except ImportError as e:
        print(f"\n❌ API import failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("VBoarder Backend Import Verification")
    print("=" * 60)
    print()

    # Test 1: Agent imports
    if not test_imports():
        sys.exit(1)

    # Test 2: API imports
    if not test_api_imports():
        sys.exit(1)

    # Test 3: Prompt building (async)
    if not asyncio.run(test_prompt_building()):
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Backend ready to start!")
    print("=" * 60)
    print("\nStart backend with:")
    print("  uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload")
    print()
