"""Aggregate samples into a portable, privacy-conscious report."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any


def percentile(values: list[float], fraction: float) -> float | None:
    """Return a nearest-rank percentile, or None when no samples are available."""
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


def build_report(
    *,
    endpoint: str,
    model: str,
    request_count: int,
    concurrency: int,
    warmup_count: int,
    wall_time_seconds: float,
    results: list[dict[str, Any]],
    python_version: str,
    platform_name: str,
) -> dict[str, Any]:
    successful = [sample for sample in results if sample["ok"]]
    latencies = [sample["latency_seconds"] for sample in successful]
    completion_tokens = [
        sample["completion_tokens"]
        for sample in successful
        if sample.get("completion_tokens") is not None
    ]
    prompt_tokens = [
        sample["prompt_tokens"]
        for sample in successful
        if sample.get("prompt_tokens") is not None
    ]
    completion_total = sum(completion_tokens) if completion_tokens else None
    prompt_total = sum(prompt_tokens) if prompt_tokens else None

    return {
        "schema_version": 1,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "model": model,
        "workload": {
            "request_count": request_count,
            "concurrency": concurrency,
            "warmup_count": warmup_count,
        },
        "environment": {"python": python_version, "platform": platform_name},
        "summary": {
            "success_count": len(successful),
            "failure_count": request_count - len(successful),
            "wall_time_seconds": wall_time_seconds,
            "latency_seconds": {
                "mean": sum(latencies) / len(latencies) if latencies else None,
                "p50": percentile(latencies, 0.50),
                "p95": percentile(latencies, 0.95),
            },
            "requests_per_second": (
                len(successful) / wall_time_seconds if wall_time_seconds > 0 else None
            ),
            "prompt_tokens": prompt_total,
            "completion_tokens": completion_total,
            "output_tokens_per_second": (
                completion_total / wall_time_seconds
                if completion_total is not None and wall_time_seconds > 0
                else None
            ),
        },
        "samples": results,
    }
