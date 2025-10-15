#!/usr/bin/env python3
"""
VBoarder Reasoning Kernel Evaluation Script
Tests multi-agent reasoning capabilities with real tasks.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx


async def test_reasoning_endpoint():
    """Test the /ask reasoning endpoint with various agent tasks."""

    test_cases = [
        {
            "name": "COO: Ops Scheduling",
            "agent": "COO",
            "task": "Schedule weekly ops sync without conflicts and ensure tasks are done before end-of-quarter deadline.",
            "max_iterations": 3,
        },
        {
            "name": "CTO: Tech Risk Assessment",
            "agent": "CTO",
            "task": "Identify top 3 technical risks in our current architecture and propose mitigation strategies.",
            "max_iterations": 4,
        },
        {
            "name": "CEO: Simple Query",
            "agent": "CEO",
            "task": "What are our strategic priorities?",
            "max_iterations": 2,
        },
        {
            "name": "CFO: Budget Analysis",
            "agent": "CFO",
            "task": "Analyze Q4 budget allocation and identify optimization opportunities.",
            "max_iterations": 5,
        },
    ]

    results = []
    base_url = "http://127.0.0.1:3738"

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Check if backend is running
        try:
            health = await client.get(f"{base_url}/health")
            if health.status_code != 200:
                print(f"❌ Backend not healthy: {health.status_code}")
                return
        except Exception as e:
            print(f"❌ Cannot connect to backend: {e}")
            print(f"   Make sure backend is running on {base_url}")
            return

        print("🧪 Testing Reasoning Kernel\n")
        print("=" * 80)

        for test_case in test_cases:
            print(f"\n🎯 Test: {test_case['name']}")
            print(f"   Agent: {test_case['agent']}")
            print(f"   Task: {test_case['task']}")
            print(f"   Max iterations: {test_case['max_iterations']}")

            try:
                response = await client.post(
                    f"{base_url}/ask",
                    json={
                        "task": test_case["task"],
                        "agent_role": test_case["agent"],
                        "max_iterations": test_case["max_iterations"],
                        "confidence_threshold": 0.85,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Status: {data['reasoning_status']}")
                    print(f"   🔁 Iterations: {data['iterations']}")
                    print(f"   📊 Confidence: {data['confidence']:.2f}")
                    print(f"   🎯 Model slot: {data['routing']['slot']}")
                    print("   📝 Result (first 200 chars):")
                    print(f"      {data['result'][:200]}...")

                    results.append(
                        {
                            "test": test_case["name"],
                            "status": "success",
                            "iterations": data["iterations"],
                            "confidence": data["confidence"],
                            "reasoning_status": data["reasoning_status"],
                        }
                    )
                else:
                    print(f"   ❌ Error: {response.status_code}")
                    print(f"      {response.text}")
                    results.append(
                        {
                            "test": test_case["name"],
                            "status": "error",
                            "error_code": response.status_code,
                        }
                    )

            except Exception as e:
                print(f"   ❌ Exception: {e}")
                results.append(
                    {"test": test_case["name"], "status": "exception", "error": str(e)}
                )

    # Save results
    output_dir = Path(__file__).parent.parent / "out"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "reasoning_eval.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print("\n📊 Summary:")
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"   ✅ Successful: {success_count}/{len(results)}")
    print(f"   📁 Results saved to: {output_file}")

    # Print detailed summary
    if success_count > 0:
        avg_iterations = sum(
            r.get("iterations", 0) for r in results if r["status"] == "success"
        ) / success_count
        avg_confidence = sum(
            r.get("confidence", 0.0) for r in results if r["status"] == "success"
        ) / success_count
        print(f"\n   📈 Average iterations: {avg_iterations:.1f}")
        print(f"   📈 Average confidence: {avg_confidence:.2f}")


async def test_simple_query():
    """Quick smoke test with a simple query."""
    print("🔥 Quick Smoke Test\n")

    base_url = "http://127.0.0.1:3738"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{base_url}/ask",
                json={
                    "task": "Say hello in 5 words or less",
                    "agent_role": "CEO",
                    "max_iterations": 2,
                },
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {data['reasoning_status']}")
                print(f"📝 Result: {data['result']}")
                print(f"🔁 Iterations: {data['iterations']}")
                print(f"📊 Confidence: {data['confidence']:.2f}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"❌ Exception: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test VBoarder reasoning kernel")
    parser.add_argument(
        "--quick", action="store_true", help="Run quick smoke test only"
    )
    args = parser.parse_args()

    if args.quick:
        asyncio.run(test_simple_query())
    else:
        asyncio.run(test_reasoning_endpoint())
