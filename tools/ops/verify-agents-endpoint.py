#!/usr/bin/env python3
"""
Quick verification script to test /agents endpoint structure
Run with: python verify_agents_endpoint.py
"""

from fastapi.testclient import TestClient

from api.main import app


def test_agents_endpoint():
    """Test that /agents endpoint works correctly"""
    client = TestClient(app)

    print("🔍 Testing /agents endpoint...")
    response = client.get("/agents")

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert "agents" in data, "Response missing 'agents' key"
    assert "count" in data, "Response missing 'count' key"
    assert isinstance(data["agents"], list), "agents should be a list"
    assert len(data["agents"]) > 0, "agents list should not be empty"
    assert data["count"] == len(data["agents"]), "count should match agents length"

    print(f"✅ SUCCESS: Found {data['count']} agents")
    print(f"✅ Agents: {', '.join(data['agents'])}")

    return True


if __name__ == "__main__":
    try:
        test_agents_endpoint()
        print("\n🎉 All checks passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
