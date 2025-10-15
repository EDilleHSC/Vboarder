"""
Development metrics endpoint for beta testing.
Track agent response latency, status codes, and quality ratings.
"""

import time

from fastapi import APIRouter

router = APIRouter(tags=["dev"])

# In-memory metrics store (dev only - not production ready)
_metrics = {"counts": {}, "sum_latency": {}, "last": []}


@router.post("/telemetry")
def telemetry(
    agent: str,
    latency_ms: int,
    status: int,
    thumbs: int | None = None,
    tag: str | None = None,
):
    """
    Record telemetry data for an agent interaction.

    Args:
        agent: Agent role (CEO, CTO, etc.)
        latency_ms: Response time in milliseconds
        status: HTTP status code
        thumbs: Optional rating (1=up, -1=down)
        tag: Optional categorization (Helpful, Off-topic, etc.)
    """
    c = _metrics["counts"].get(agent, 0) + 1
    _metrics["counts"][agent] = c
    _metrics["sum_latency"][agent] = _metrics["sum_latency"].get(agent, 0) + latency_ms
    _metrics["last"].append(
        {
            "ts": int(time.time()),
            "agent": agent,
            "latency_ms": latency_ms,
            "status": status,
            "thumbs": thumbs,
            "tag": tag,
        }
    )
    # Keep only last 200 entries
    _metrics["last"] = _metrics["last"][-200:]
    return {"ok": True}


@router.get("/metrics")
def metrics():
    """
    Get aggregated metrics for all agents.

    Returns:
        - p50_guess: Rough average latency per agent
        - count: Total requests per agent
        - last: Last 200 telemetry events
    """
    out = {"p50_guess": {}, "count": _metrics["counts"]}
    for a, total in _metrics["sum_latency"].items():
        c = max(_metrics["counts"].get(a, 1), 1)
        out["p50_guess"][a] = int(total / c)
    out["last"] = _metrics["last"]
    return out
