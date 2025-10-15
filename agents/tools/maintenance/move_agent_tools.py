import os
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")

# Create /tools directory if it doesn't exist
os.makedirs(TOOLS_DIR, exist_ok=True)

# Extensions to move
EXTENSIONS_TO_MOVE = {".py", ".ps1", ".md", ".json", ".txt"}

# Agent folders to skip (assumes top-level folders with 3-letter roles)
AGENT_FOLDERS = {
    "AIR", "CEO", "CFO", "COO", "CMO", "CLO", "COS", "CTO", "SEC", "backups"
}

# Files to exclude explicitly
EXCLUDE_FILES = {"agent_registry.json"}

moved_files = []

for filename in os.listdir(ROOT_DIR):
    src_path = os.path.join(ROOT_DIR, filename)
    
    # Skip folders (agents) and unwanted files
    if os.path.isdir(src_path) and filename in AGENT_FOLDERS:
        continue
    if filename in EXCLUDE_FILES:
        continue

    _, ext = os.path.splitext(filename)
    if ext.lower() in EXTENSIONS_TO_MOVE:
        dst_path = os.path.join(TOOLS_DIR, filename)
        shutil.move(src_path, dst_path)
        moved_files.append(filename)

# 🎉 Result
print("✅ Agent tools moved to /tools/")
for f in moved_files:
    print(f"   └─ 📁 {f}")
