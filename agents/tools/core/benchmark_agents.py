#!/usr/bin/env python3
import os
import time
import json

AGENTS_DIR = "../agents/"
LOG_PATH = "./logs/benchmark_log.json"

os.makedirs("logs", exist_ok=True)

def benchmark_agents():
    print("⚙️ Benchmarking agents...")

    results = {}

    if not os.path.exists(AGENTS_DIR):
        print(f"❌ Agents directory not found: {AGENTS_DIR}")
        return

    for agent_name in os.listdir(AGENTS_DIR):
        agent_path = os.path.join(AGENTS_DIR, agent_name)
        if os.path.isdir(agent_path):
            start = time.time()
            time.sleep(0.5)  # Simulated workload
            end = time.time()

            results[agent_name] = {
                "benchmark_duration_sec": round(end - start, 3)
            }

    with open(LOG_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Benchmark results saved to: {LOG_PATH}")

if __name__ == "__main__":
    benchmark_agents()
