"""Command-line benchmark for remote OpenAI-compatible chat APIs."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any


DEFAULT_PROMPT = "In a few sentences, explain how mixture-of-experts models route tokens."


def percentile(values: list[float], fraction: float) -> float | None:
    """Return a nearest-rank percentile, or None when there are no samples."""
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trillion-bench",
        description="Measure a remote OpenAI-compatible chat-completions endpoint.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="run repeated completion requests")
    run.add_argument("--base-url", required=True, help="API base URL, for example https://host.example/v1")
    run.add_argument("--model", required=True, help="provider model ID")
    run.add_argument("--prompt", default=DEFAULT_PROMPT, help="user prompt sent on every request")
    run.add_argument("--requests", type=int, default=5, help="number of sequential requests (default: 5)")
    run.add_argument("--max-tokens", type=int, default=128, help="maximum generated tokens per request")
    run.add_argument("--temperature", type=float, default=0.0, help="sampling temperature")
    run.add_argument("--timeout", type=float, default=120.0, help="per-request timeout in seconds")
    run.add_argument("--api-key-env", help="environment variable containing the provider API key")
    run.add_argument("--output", help="optional path for a JSON results file")
    return parser


def endpoint_url(base_url: str) -> str:
    return base_url.rstrip("/") + "/chat/completions"


def send_request(
    url: str,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    api_key: str | None,
    timeout: float,
) -> dict[str, Any]:
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
    ).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            status = response.status
        elapsed = time.perf_counter() - started
        parsed = json.loads(body.decode("utf-8"))
        usage = parsed.get("usage") or {}
        return {
            "ok": True,
            "latency_seconds": elapsed,
            "status_code": status,
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
        }
    except urllib.error.HTTPError as exc:
        elapsed = time.perf_counter() - started
        # Do not include response bodies: providers can echo sensitive request data.
        return {"ok": False, "latency_seconds": elapsed, "status_code": exc.code, "error": f"HTTP {exc.code}"}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        elapsed = time.perf_counter() - started
        return {"ok": False, "latency_seconds": elapsed, "error": type(exc).__name__}


def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    if args.requests < 1:
        raise ValueError("--requests must be at least 1")
    if args.max_tokens < 1:
        raise ValueError("--max-tokens must be at least 1")
    if args.timeout <= 0:
        raise ValueError("--timeout must be greater than 0")
    if not 0 <= args.temperature <= 2:
        raise ValueError("--temperature must be between 0 and 2")

    api_key = os.environ.get(args.api_key_env) if args.api_key_env else None
    url = endpoint_url(args.base_url)
    print(f"Sending {args.requests} sequential request(s) to {url}", file=sys.stderr)
    started = time.perf_counter()
    results = [
        send_request(
            url=url,
            model=args.model,
            prompt=args.prompt,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            api_key=api_key,
            timeout=args.timeout,
        )
        for _ in range(args.requests)
    ]
    wall_seconds = time.perf_counter() - started

    successful = [result for result in results if result["ok"]]
    latencies = [result["latency_seconds"] for result in successful]
    completion_values = [
        result["completion_tokens"]
        for result in successful
        if isinstance(result.get("completion_tokens"), (int, float))
    ]
    prompt_values = [
        result["prompt_tokens"]
        for result in successful
        if isinstance(result.get("prompt_tokens"), (int, float))
    ]
    total_completion_tokens = sum(completion_values) if completion_values else None
    total_prompt_tokens = sum(prompt_values) if prompt_values else None

    return {
        "schema_version": 1,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": url,
        "model": args.model,
        "request_count": args.requests,
        "success_count": len(successful),
        "failure_count": args.requests - len(successful),
        "wall_time_seconds": wall_seconds,
        "latency_seconds": {
            "mean": sum(latencies) / len(latencies) if latencies else None,
            "p50": percentile(latencies, 0.50),
            "p95": percentile(latencies, 0.95),
        },
        "requests_per_second": len(successful) / wall_seconds if wall_seconds > 0 else None,
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
        "output_tokens_per_second": (
            total_completion_tokens / wall_seconds
            if total_completion_tokens is not None and wall_seconds > 0
            else None
        ),
        "results": results,
    }


def print_summary(report: dict[str, Any]) -> None:
    latencies = report["latency_seconds"]
    print(f"Model: {report['model']}")
    print(f"Requests: {report['success_count']} succeeded, {report['failure_count']} failed")
    print(f"Wall time: {report['wall_time_seconds']:.3f}s")
    if latencies["mean"] is not None:
        print(
            "Latency: mean {mean:.3f}s | p50 {p50:.3f}s | p95 {p95:.3f}s".format(
                mean=latencies["mean"], p50=latencies["p50"], p95=latencies["p95"]
            )
        )
    else:
        print("Latency: no successful samples")
    rate = report["requests_per_second"]
    print(f"Requests/sec: {rate:.3f}" if rate is not None else "Requests/sec: n/a")
    token_rate = report["output_tokens_per_second"]
    print(f"Output tokens/sec: {token_rate:.3f}" if token_rate is not None else "Output tokens/sec: n/a (provider usage unavailable)")


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    try:
        report = run_benchmark(args)
    except ValueError as exc:
        parser.error(str(exc))
    print_summary(report)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as output_file:
            json.dump(report, output_file, indent=2)
            output_file.write("\n")
        print(f"JSON report saved to {args.output}")

    return 0 if report["success_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
