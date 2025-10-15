#!/usr/bin/env python3
import os
import json

LOG_PATH = "./logs/install_policy_log.json"
POLICY = {
    "enforce_zero_trust": True,
    "audit_trail": True,
    "allowed_roles": ["admin", "ops"],
}

os.makedirs("logs", exist_ok=True)

def install_policy():
    # Fake installation process
    print("📦 Injecting core policy into agent config...")
    with open(LOG_PATH, "w") as f:
        json.dump(POLICY, f, indent=2)
    print(f"✅ Policy injected and saved to: {LOG_PATH}")

if __name__ == "__main__":
    install_policy()
