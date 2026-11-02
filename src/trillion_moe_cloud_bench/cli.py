"""Command-line interface for remote inference benchmarks."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .client import endpoint_url, send_request
from .metrics import build_report


DEFAULT_PROMPT = "In a few sentences, explain how mixture-of-experts models route tokens."


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trillion-bench",
        description="Measure a remote OpenAI-compatible chat-completions endpoint.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="run a bounded completion benchmark")
    run.add_argument("--base-url", required=True, help="API base URL, for example https://host.example/v1")
    run.add_argument("--model", required=True, help="provider model ID")
    run.add_argument("--prompt", default=DEFAULT_PROMPT, help="user prompt sent for every request")
    run.add_argument("--requests", type=int, default=5, help="measured requests (default: 5)")
    run.add_argument("--concurrency", type=int, default=1, help="maximum simultaneous requests (default: 1)")
    run.add_argument("--warmup", type=int, default=0, help="unreported warm-up requests before measurement")
    run.add_argument("--max-tokens", type=int, default=128, help="maximum generated tokens per request")
    run.add_argument("--temperature", type=float, default=0.0, help="sampling temperature")
    run.add_argument("--timeout", type=float, default=120.0, help="per-request timeout in seconds")
    run.add_argument("--api-key-env", help="environment variable containing the provider API key")
    run.add_argument("--output", help="optional path for a JSON results file")
    return parser


def _safe_endpoint(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _validate(args: argparse.Namespace) -> None:
    if not args.model.strip():
        raise ValueError("--model must not be empty")
    if not args.prompt:
        raise ValueError("--prompt must not be empty")
    if args.requests < 1:
        raise ValueError("--requests must be at least 1")
    if args.concurrency < 1 or args.concurrency > 64:
        raise ValueError("--concurrency must be between 1 and 64")
    if args.warmup < 0 or args.warmup > 20:
        raise ValueError("--warmup must be between 0 and 20")
    if args.max_tokens < 1:
        raise ValueError("--max-tokens must be at least 1")
    if args.timeout <= 0:
        raise ValueError("--timeout must be greater than 0")
    if not 0 <= args.temperature <= 2:
        raise ValueError("--temperature must be between 0 and 2")


def _make_sender(args: argparse.Namespace, url: str, api_key: str | None):
    def send() -> dict[str, Any]:
        return send_request(
            url=url,
            model=args.model,
            prompt=args.prompt,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            api_key=api_key,
            timeout=args.timeout,
        )
    return send


def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    _validate(args)
    api_key = None
    if args.api_key_env:
        api_key = os.environ.get(args.api_key_env)
        if not api_key:
            raise ValueError(f"environment variable {args.api_key_env!r} is not set or is empty")

    url = endpoint_url(args.base_url)
    send = _make_sender(args, url, api_key)
    print(
        f"Warm-ups: {args.warmup} | measured requests: {args.requests} | "
        f"concurrency: {args.concurrency}",
        file=sys.stderr,
    )

    # Warm-ups are explicit provider calls and may be billable.
    for warmup_index in range(args.warmup):
        result = send()
        if not result["ok"]:
            print(f"Warm-up {warmup_index + 1} failed: {result.get('error', 'request_error')}", file=sys.stderr)

    started_at = datetime.now(timezone.utc).isoformat()
    wall_started = time.perf_counter()
    results: list[dict[str, Any] | None] = [None] * args.requests
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {pool.submit(send): index for index in range(args.requests)}
        for future in as_completed(futures):
            index = futures[future]
            try:
                results[index] = {"request_index": index + 1, **future.result()}
            except Exception as exc:
                results[index] = {
                    "request_index": index + 1,
                    "ok": False,
                    "latency_seconds": 0.0,
                    "error": type(exc).__name__,
                }
    wall_seconds = time.perf_counter() - wall_started
    samples = [sample for sample in results if sample is not None]

    report = build_report(
        endpoint=_safe_endpoint(url),
        model=args.model,
        request_count=args.requests,
        concurrency=args.concurrency,
        warmup_count=args.warmup,
        wall_time_seconds=wall_seconds,
        results=samples,
        python_version=platform.python_version(),
        platform_name=platform.system(),
    )
    report["started_at"] = started_at
    return report


def print_summary(report: dict[str, Any]) -> None:
    summary = report["summary"]
    latency = summary["latency_seconds"]
    print(f"Model: {report['model']}")
    print(f"Requests: {summary['success_count']} succeeded, {summary['failure_count']} failed")
    print(f"Wall time: {summary['wall_time_seconds']:.3f}s")
    if latency["mean"] is not None:
        print(
            "Latency: mean {mean:.3f}s | p50 {p50:.3f}s | p95 {p95:.3f}s".format(
                mean=latency["mean"], p50=latency["p50"], p95=latency["p95"]
            )
        )
    else:
        print("Latency: no successful samples")
    rate = summary["requests_per_second"]
    print(f"Requests/sec: {rate:.3f}" if rate is not None else "Requests/sec: n/a")
    token_rate = summary["output_tokens_per_second"]
    print(
        f"Output tokens/sec: {token_rate:.3f}"
        if token_rate is not None
        else "Output tokens/sec: n/a (provider usage unavailable)"
    )


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

    return 0 if report["summary"]["success_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
