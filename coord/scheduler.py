import os
import time
import subprocess

AGENTS = ["CEO", "CTO", "CFO", "CLO", "CMO", "COO", "COS", "SEC"]
INTERVAL = int(os.environ.get("INTERVAL", 60))

def run_sync_cycle(agent):
    print(f"\n🔄 Running sync for: {agent}")
    env = os.environ.copy()
    env["AGENT"] = agent
    try:
        if agent == "CEO":
            subprocess.run(["python3", "coord/ceo_sync.py"], check=True, env=env)
        else:
            subprocess.run(["python3", "coord/agent_sync.py"], check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"❌ Sync failed for {agent}: {e}")

if __name__ == "__main__":
    print(f"🗓️  Agent scheduler started (interval: {INTERVAL} seconds)")
    while True:
        for agent in AGENTS:
            run_sync_cycle(agent)
        print(f"⏳ Sleeping for {INTERVAL}s before next cycle...\n")
        time.sleep(INTERVAL)
