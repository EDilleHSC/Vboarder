#!/usr/bin/env python3
"""
📊 VBoarder Eval Results Viewer
Log viewer and metrics CLI for assessing model confidence trends and performance.
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class EvalViewer:
    """Viewer for evaluation results and confidence metrics."""

    def __init__(self):
        self.conversation_dir = Path("data/conversations")
        self.memory_file = Path("data/memory.jsonl")
        self.agent_dirs = Path("agents")

    def load_conversations(self, days_back: int = 7) -> list[dict[str, Any]]:
        """Load recent conversations from all agents."""
        conversations = []

        if not self.conversation_dir.exists():
            return conversations

        cutoff_date = datetime.now() - timedelta(days=days_back)

        for conv_file in self.conversation_dir.glob("*.jsonl"):
            try:
                with open(conv_file) as f:
                    for line in f:
                        if line.strip():
                            conv = json.loads(line)
                            conv_time = datetime.fromisoformat(
                                conv["timestamp"].replace("Z", "+00:00").replace("+00:00", "")
                            )

                            if conv_time >= cutoff_date:
                                conv["agent_role"] = self._extract_agent_from_filename(conv_file.name)
                                conv["file"] = conv_file.name
                                conversations.append(conv)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"⚠️  Error reading {conv_file}: {e}")

        return sorted(conversations, key=lambda x: x["timestamp"])

    def _extract_agent_from_filename(self, filename: str) -> str:
        """Extract agent role from conversation filename."""
        # Pattern: default_CEO.jsonl -> CEO
        match = re.search(r"_([A-Z]+)\.jsonl$", filename)
        return match.group(1) if match else "UNKNOWN"

    def analyze_conversation_patterns(self, conversations: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze conversation patterns and extract metrics."""
        if not conversations:
            return {}

        # Group by agent
        by_agent = {}
        for conv in conversations:
            agent = conv["agent_role"]
            if agent not in by_agent:
                by_agent[agent] = []
            by_agent[agent].append(conv)

        # Calculate metrics
        metrics = {
            "total_conversations": len(conversations),
            "unique_agents": len(by_agent),
            "by_agent": {},
            "time_range": {"start": conversations[0]["timestamp"], "end": conversations[-1]["timestamp"]},
            "response_length_stats": self._calculate_response_lengths(conversations),
        }

        for agent, convs in by_agent.items():
            metrics["by_agent"][agent] = {
                "count": len(convs),
                "avg_response_length": sum(len(c.get("agent", "")) for c in convs) / len(convs),
                "recent_activity": convs[-1]["timestamp"] if convs else None,
            }

        return metrics

    def _calculate_response_lengths(self, conversations: list[dict[str, Any]]) -> dict[str, float]:
        """Calculate response length statistics."""
        lengths = [len(conv.get("agent", "")) for conv in conversations]
        if not lengths:
            return {}

        lengths.sort()
        n = len(lengths)

        return {
            "min": min(lengths),
            "max": max(lengths),
            "avg": sum(lengths) / n,
            "median": lengths[n // 2],
            "total_chars": sum(lengths),
        }

    def simulate_confidence_analysis(self, conversations: list[dict[str, Any]]) -> dict[str, Any]:
        """Simulate confidence analysis based on response characteristics."""
        confidence_data = []

        for conv in conversations:
            response = conv.get("agent", "")

            # Heuristic confidence scoring (similar to scorer_stub.py)
            confidence = self._estimate_confidence(response)

            confidence_data.append(
                {
                    "timestamp": conv["timestamp"],
                    "agent": conv["agent_role"],
                    "confidence": confidence,
                    "response_length": len(response),
                    "estimated": True,  # Mark as estimated
                }
            )

        # Calculate trends
        if confidence_data:
            confidences = [c["confidence"] for c in confidence_data]
            return {
                "data": confidence_data,
                "summary": {
                    "avg_confidence": sum(confidences) / len(confidences),
                    "min_confidence": min(confidences),
                    "max_confidence": max(confidences),
                    "total_samples": len(confidences),
                    "low_confidence_count": sum(1 for c in confidences if c < 0.6),
                    "high_confidence_count": sum(1 for c in confidences if c > 0.8),
                },
            }

        return {"data": [], "summary": {}}

    def _estimate_confidence(self, response: str) -> float:
        """Estimate confidence based on response characteristics."""
        if not response:
            return 0.0

        score = 0.75  # Base confidence

        # Positive indicators
        if len(response) > 100:
            score += 0.05
        if any(phrase in response.lower() for phrase in ["based on", "analysis", "data shows", "research indicates"]):
            score += 0.1
        if response.count(".") > 3:  # More structured response
            score += 0.05

        # Negative indicators
        uncertainty_words = ["maybe", "perhaps", "might", "unclear", "unsure", "probably"]
        uncertainty_count = sum(response.lower().count(word) for word in uncertainty_words)
        score -= uncertainty_count * 0.1

        # Error indicators
        if any(word in response.lower() for word in ["error", "failed", "cannot", "unable"]):
            score -= 0.2

        return max(0.0, min(1.0, score))

    def display_summary(self, days_back: int = 7):
        """Display comprehensive summary of recent activity."""
        print(f"📊 VBoarder Eval Results Summary (Last {days_back} days)")
        print("=" * 60)

        # Load data
        conversations = self.load_conversations(days_back)
        if not conversations:
            print("❌ No conversations found in the specified time range")
            return

        # Analyze patterns
        metrics = self.analyze_conversation_patterns(conversations)
        confidence_analysis = self.simulate_confidence_analysis(conversations)

        # Display conversation metrics
        print("\n💬 Conversation Metrics:")
        print(f"   📈 Total conversations: {metrics['total_conversations']}")
        print(f"   🤖 Active agents: {metrics['unique_agents']}")
        print(f"   📅 Time range: {metrics['time_range']['start'][:10]} to {metrics['time_range']['end'][:10]}")

        # Response length stats
        if metrics["response_length_stats"]:
            stats = metrics["response_length_stats"]
            print(f"   📝 Response lengths: avg={stats['avg']:.0f}, min={stats['min']}, max={stats['max']}")

        # Agent breakdown
        print("\n🤖 Agent Activity Breakdown:")
        for agent, data in metrics["by_agent"].items():
            print(f"   {agent}: {data['count']} conversations, avg {data['avg_response_length']:.0f} chars")

        # Confidence analysis (simulated)
        if confidence_analysis["summary"]:
            conf_sum = confidence_analysis["summary"]
            print("\n🎯 Confidence Analysis (Estimated):")
            print(f"   📊 Average confidence: {conf_sum['avg_confidence']:.2f}")
            print(f"   📈 Range: {conf_sum['min_confidence']:.2f} - {conf_sum['max_confidence']:.2f}")
            print(f"   🔴 Low confidence (<0.6): {conf_sum['low_confidence_count']}")
            print(f"   🟢 High confidence (>0.8): {conf_sum['high_confidence_count']}")

    def display_confidence_trends(self, agent: str | None = None, limit: int = 20):
        """Display recent confidence trends."""
        conversations = self.load_conversations()
        confidence_analysis = self.simulate_confidence_analysis(conversations)

        if not confidence_analysis["data"]:
            print("❌ No confidence data available")
            return

        # Filter by agent if specified
        data = confidence_analysis["data"]
        if agent:
            data = [d for d in data if d["agent"] == agent.upper()]
            if not data:
                print(f"❌ No data found for agent {agent}")
                return

        # Show recent trends
        recent_data = data[-limit:]

        print(f"📈 Recent Confidence Trends{'for ' + agent if agent else ''} (Last {len(recent_data)})")
        print("-" * 60)

        for item in recent_data:
            conf_icon = "🟢" if item["confidence"] > 0.8 else "🟡" if item["confidence"] > 0.6 else "🔴"
            time_str = item["timestamp"][:19].replace("T", " ")
            print(
                f"{conf_icon} {time_str} | {item['agent']:3} | {item['confidence']:.2f} | {item['response_length']:4d} chars"
            )

    def export_metrics(self, output_file: str = "eval_metrics.json"):
        """Export metrics to JSON file."""
        conversations = self.load_conversations()
        metrics = self.analyze_conversation_patterns(conversations)
        confidence_analysis = self.simulate_confidence_analysis(conversations)

        export_data = {
            "generated_at": datetime.now().isoformat(),
            "conversation_metrics": metrics,
            "confidence_analysis": confidence_analysis,
            "data_sources": {
                "conversation_dir": str(self.conversation_dir),
                "memory_file": str(self.memory_file),
            },
        }

        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2)

        print(f"📁 Metrics exported to {output_file}")


def main():
    """Main CLI interface."""
    viewer = EvalViewer()

    if len(sys.argv) == 1:
        viewer.display_summary()
    elif sys.argv[1] == "trends":
        agent = sys.argv[2] if len(sys.argv) > 2 else None
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        viewer.display_confidence_trends(agent, limit)
    elif sys.argv[1] == "export":
        output = sys.argv[2] if len(sys.argv) > 2 else "eval_metrics.json"
        viewer.export_metrics(output)
    elif sys.argv[1] == "summary":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        viewer.display_summary(days)
    else:
        print("📊 VBoarder Eval Results Viewer")
        print("Usage:")
        print("  python eval_viewer.py                    # Show summary")
        print("  python eval_viewer.py summary [days]     # Show summary for N days")
        print("  python eval_viewer.py trends [agent] [limit] # Show confidence trends")
        print("  python eval_viewer.py export [file]      # Export metrics to JSON")
        print("\nExamples:")
        print("  python eval_viewer.py trends CEO 10      # Show last 10 CEO trends")
        print("  python eval_viewer.py summary 14         # Show 14-day summary")


if __name__ == "__main__":
    main()
