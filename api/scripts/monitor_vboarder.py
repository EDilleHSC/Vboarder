import json
import time

from embedding_health import check_embedding_service
from gpu_health import log_gpu_metrics
from ingestion_health import check_ingestion_health
from qdrant_health import check_qdrant


def log(data, filename):
    with open(filename, "a") as f:
        f.write(json.dumps(data) + "\n")


def main():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Starting VBoarder system health check...")

    results = {
        "timestamp": timestamp,
        "ingestion": check_ingestion_health(),
        "embedding": check_embedding_service(),
        "qdrant": check_qdrant(),
        "gpu": log_gpu_metrics(),
    }

    log(results, "vboarder_monitor_log.jsonl")
    print("✓ Monitoring complete.")


if __name__ == "__main__":
    main()
