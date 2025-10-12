# File: scripts/next_shift_monitoring.py

import os
import time
import json
import subprocess
import requests
from datetime import datetime
from qdrant_client import QdrantClient

# Config
OLLAMA_URL = "http://localhost:11434"  # Local Ollama API
QDRANT_URL = "http://localhost:6333"
AGENT = "CEO"
LOG_DIR = "logs"

# Ensure log dir exists
os.makedirs(LOG_DIR, exist_ok=True)

def log_json(obj, tag):
    now = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(LOG_DIR, f"{tag}_{now}.json")
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    print(f"[LOGGED] {tag} -> {path}")

def check_ollama():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags")
        r.raise_for_status()
        return {"status": "ok", "models": r.json()}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_qdrant():
    try:
        q = QdrantClient(host="localhost", port=6333)
        colls = q.get_collections()
        return {"status": "ok", "collections": [c.name for c in colls.collections]}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def get_gpu_info():
    try:
        result = subprocess.check_output(["nvidia-smi", "--query-gpu=temperature.gpu,memory.used", "--format=csv,noheader,nounits"])
        temp, mem = result.decode().strip().split(', ')
        return {"temperature_C": int(temp), "memory_MB": int(mem)}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def run_monitoring():
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": AGENT,
        "ollama": check_ollama(),
        "qdrant": check_qdrant(),
        "gpu": get_gpu_info()
    }
    log_json(report, "shift_monitor")

if __name__ == "__main__":
    run_monitoring()
