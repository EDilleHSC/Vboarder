import json
import os
from pathlib import Path
from datetime import datetime

# --- Configuration (using pathlib) ---
# Resolve the script's directory, assuming agents are in the parent folder
SCRIPT_DIR = Path(__file__).resolve().parent
AGENT_ROOT = SCRIPT_DIR.parent / "agents"

AGENT_FIELDS = ["agent.json", "persona.md", "prompt.md", "README.md"]
OPTIONAL_DIRS = ["memory", "logs", "config"]


def load_json_safely(path: Path):
    """Safely loads a JSON file, handling UTF-8 BOM."""
    try:
        # Use 'utf-8-sig' to strip the Byte Order Mark (BOM)
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        return f"❌ {str(e)}"
    
    
def scan_agents():
    # 1. Use pathlib to find directories and filter out non-agent folders
    agents = [
        d.name for d in AGENT_ROOT.iterdir()
        if d.is_dir() and d.name not in ["logs", "Clean", "tools", "agent_runtime"]
    ]
    
    summary = {}
    for agent_name in agents:
        agent_path = AGENT_ROOT / agent_name
        log = {
            "required_files": {},
            "optional_dirs": {},
            "memory_contents": []
        }

        # 2. Check required files (Pathlib simplifies joining and checking)
        for f in AGENT_FIELDS:
            fpath = agent_path / f
            log["required_files"][f] = "✅" if fpath.is_file() else "❌ MISSING"

        # 3. Check subdirs and memory contents
        for subdir in OPTIONAL_DIRS:
            sub_path = agent_path / subdir
            
            if sub_path.is_dir():
                log["optional_dirs"][subdir] = "✅ Present"
                
                if subdir == "memory":
                    # Check JSON validity for files in memory folder
                    for mem_file in sub_path.iterdir():
                        if mem_file.is_file():
                            result = load_json_safely(mem_file)
                            if isinstance(result, str) and result.startswith("❌"):
                                log["memory_contents"].append(f"{mem_file.name}: {result}")
                            else:
                                log["memory_contents"].append(f"{mem_file.name}: ✅ valid JSON")
            else:
                log["optional_dirs"][subdir] = "❌ MISSING"

        summary[agent_name] = log

    return summary


def save_audit_report(report):
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = AGENT_ROOT.parent / f"agent_logic_audit_{now}.json" # Save report outside agents dir
    
    # Use 'utf-8' encoding for output consistency
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"✅ Logic audit report saved to {out_path}")


if __name__ == "__main__":
    result = scan_agents()
    save_audit_report(result)