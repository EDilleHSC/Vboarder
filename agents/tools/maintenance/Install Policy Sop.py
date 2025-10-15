import os
import shutil

# === CONFIG ===
AGENT_ROOT = "/mnt/d/ai/projects/vboarder/agents"
POLICY_FILE = "POLICY_SOP.md"
EXCLUDE_DIRS = {"logs", "backups", "Clean"}

# === MAIN ===
def install_policy_to_agents():
    policy_path = os.path.join(AGENT_ROOT, POLICY_FILE)
    if not os.path.exists(policy_path):
        print(f"❌ Missing {POLICY_FILE} in root. Aborting.")
        return

    print(f"📄 Found policy file: {policy_path}\n")

    for agent_name in os.listdir(AGENT_ROOT):
        agent_path = os.path.join(AGENT_ROOT, agent_name)
        if not os.path.isdir(agent_path) or agent_name in EXCLUDE_DIRS:
            continue

        dest_path = os.path.join(agent_path, POLICY_FILE)
        shutil.copy(policy_path, dest_path)
        print(f"✅ Installed policy to: {agent_name}/")

    print("\n🎉 Done: All agents patched with policy and SOP.")


if __name__ == "__main__":
    install_policy_to_agents()
