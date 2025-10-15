"""
Ingestion Latency Logger
Tracks document processing times with target threshold alerting
"""

import json
import statistics
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class LatencyLogger:
    def __init__(
        self, log_file: str = "ingestion_latency.jsonl", target_latency: float = 2.0
    ):
        self.log_file = Path(log_file)
        self.target_latency = target_latency  # seconds
        self.current_session = []

    @contextmanager
    def track_ingestion(
        self, doc_name: str, doc_type: str = "unknown", metadata: Dict = None
    ):
        """Context manager to track ingestion latency"""
        start_time = time.time()
        start_timestamp = datetime.now().isoformat()

        error = None
        try:
            yield
        except Exception as e:
            error = str(e)
            raise
        finally:
            elapsed = time.time() - start_time

            # Log the result
            self.log(
                doc_name=doc_name,
                doc_type=doc_type,
                latency=elapsed,
                timestamp=start_timestamp,
                error=error,
                metadata=metadata or {},
            )

    def log(
        self,
        doc_name: str,
        doc_type: str,
        latency: float,
        timestamp: str,
        error: Optional[str] = None,
        metadata: Dict = None,
    ):
        """Log a single ingestion event"""

        meets_target = latency < self.target_latency

        entry = {
            "timestamp": timestamp,
            "doc_name": doc_name,
            "doc_type": doc_type,
            "latency_seconds": round(latency, 3),
            "target_seconds": self.target_latency,
            "meets_target": meets_target,
            "error": error,
            "metadata": metadata or {},
        }

        # Add to session
        self.current_session.append(entry)

        # Write to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Print status
        status = "✅" if meets_target else "⚠️"
        if error:
            status = "❌"

        print(f"{status} {doc_name}: {latency:.3f}s (target: {self.target_latency}s)")

        if error:
            print(f"   Error: {error}")

    def get_session_stats(self) -> Dict:
        """Get statistics for current session"""
        if not self.current_session:
            return {"error": "No data in current session"}

        latencies = [
            e["latency_seconds"] for e in self.current_session if not e["error"]
        ]
        errors = [e for e in self.current_session if e["error"]]

        if not latencies:
            return {
                "total_docs": len(self.current_session),
                "errors": len(errors),
                "error_rate": 1.0,
            }

        return {
            "total_docs": len(self.current_session),
            "successful": len(latencies),
            "errors": len(errors),
            "error_rate": len(errors) / len(self.current_session),
            "latency": {
                "min": round(min(latencies), 3),
                "max": round(max(latencies), 3),
                "avg": round(statistics.mean(latencies), 3),
                "median": round(statistics.median(latencies), 3),
                "p95": (
                    round(statistics.quantiles(latencies, n=20)[18], 3)
                    if len(latencies) > 1
                    else latencies[0]
                ),
            },
            "target_compliance": {
                "target_seconds": self.target_latency,
                "docs_meeting_target": sum(
                    1 for l in latencies if l < self.target_latency
                ),
                "compliance_rate": sum(1 for l in latencies if l < self.target_latency)
                / len(latencies),
            },
        }

    def print_session_report(self):
        """Print formatted session report"""
        stats = self.get_session_stats()

        print("\n" + "=" * 60)
        print("⏱️ INGESTION LATENCY REPORT")
        print("=" * 60)

        print("\n📊 Session Overview:")
        print(f"  Total Documents: {stats['total_docs']}")
        print(f"  Successful: {stats['successful']}")
        print(f"  Errors: {stats['errors']}")

        if stats.get("latency"):
            lat = stats["latency"]
            print("\n⏱️ Latency Statistics:")
            print(f"  Min: {lat['min']}s")
            print(f"  Max: {lat['max']}s")
            print(f"  Average: {lat['avg']}s")
            print(f"  Median: {lat['median']}s")
            print(f"  P95: {lat['p95']}s")

            target = stats["target_compliance"]
            compliance_pct = target["compliance_rate"] * 100
            status = (
                "✅" if compliance_pct >= 95 else "⚠️" if compliance_pct >= 80 else "❌"
            )

            print(f"\n🎯 Target Compliance ({self.target_latency}s):")
            print(
                f"  Docs Meeting Target: {target['docs_meeting_target']}/{stats['successful']}"
            )
            print(f"  Compliance Rate: {compliance_pct:.1f}% {status}")

            if compliance_pct < 95:
                print("\n⚠️ WARNING: Target compliance below 95%")
                print("   Consider optimizing pipeline or increasing resources")

        return stats

    def analyze_log_file(self, hours: int = 24) -> Dict:
        """Analyze historical log data"""
        if not self.log_file.exists():
            return {"error": "Log file not found"}

        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        entries = []

        with open(self.log_file, "r") as f:
            for line in f:
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry["timestamp"]).timestamp()

                if entry_time >= cutoff_time:
                    entries.append(entry)

        if not entries:
            return {"error": f"No data found in last {hours} hours"}

        # Calculate stats
        latencies = [e["latency_seconds"] for e in entries if not e["error"]]
        errors = [e for e in entries if e["error"]]

        # Group by doc type
        by_type = {}
        for entry in entries:
            doc_type = entry["doc_type"]
            if doc_type not in by_type:
                by_type[doc_type] = []
            if not entry["error"]:
                by_type[doc_type].append(entry["latency_seconds"])

        type_stats = {}
        for doc_type, lats in by_type.items():
            if lats:
                type_stats[doc_type] = {
                    "count": len(lats),
                    "avg_latency": round(statistics.mean(lats), 3),
                    "compliance_rate": sum(1 for l in lats if l < self.target_latency)
                    / len(lats),
                }

        return {
            "period_hours": hours,
            "total_docs": len(entries),
            "successful": len(latencies),
            "errors": len(errors),
            "avg_latency": round(statistics.mean(latencies), 3) if latencies else None,
            "by_type": type_stats,
        }


# Example usage
if __name__ == "__main__":
    logger = LatencyLogger(target_latency=2.0)

    # Track individual documents
    with logger.track_ingestion("test.pdf", doc_type="pdf", metadata={"size_mb": 1.2}):
        # Your ingestion code here
        time.sleep(1.5)  # Simulate processing

    with logger.track_ingestion("data.csv", doc_type="csv", metadata={"rows": 10000}):
        time.sleep(0.8)  # Simulate processing

    # Print session report
    logger.print_session_report()

    # Analyze historical data
    # historical = logger.analyze_log_file(hours=24)
    # print(json.dumps(historical, indent=2))
