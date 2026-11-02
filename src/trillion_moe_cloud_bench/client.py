"""Small, dependency-free HTTP client for OpenAI-compatible endpoints."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlsplit


MAX_RESPONSE_BYTES = 10 * 1024 * 1024


def endpoint_url(base_url: str) -> str:
    """Validate a remote HTTPS URL (or loopback HTTP) and append the chat path."""
    parts = urlsplit(base_url)
    if parts.scheme not in {"https", "http"} or not parts.hostname:
        raise ValueError("--base-url must be an absolute HTTP(S) URL")
    if parts.username or parts.password:
        raise ValueError("--base-url must not contain embedded credentials")
    loopback = parts.hostname in {"localhost", "127.0.0.1", "::1"}
    if parts.scheme != "https" and not loopback:
        raise ValueError("HTTPS is required except for localhost/loopback endpoints")
    if parts.query or parts.fragment:
        raise ValueError("--base-url must not contain a query string or fragment")
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
            body = response.read(MAX_RESPONSE_BYTES + 1)
            status = response.status
        elapsed = time.perf_counter() - started
        if len(body) > MAX_RESPONSE_BYTES:
            return {"ok": False, "latency_seconds": elapsed, "status_code": status, "error": "response_too_large"}
        parsed = json.loads(body.decode("utf-8"))
        if not isinstance(parsed, dict):
            return {"ok": False, "latency_seconds": elapsed, "status_code": status, "error": "invalid_response"}
        usage = parsed.get("usage") or {}
        if not isinstance(usage, dict):
            usage = {}
        return {
            "ok": True,
            "latency_seconds": elapsed,
            "status_code": status,
            "prompt_tokens": _nonnegative_number(usage.get("prompt_tokens")),
            "completion_tokens": _nonnegative_number(usage.get("completion_tokens")),
        }
    except urllib.error.HTTPError as exc:
        elapsed = time.perf_counter() - started
        # Response bodies can echo request content; never store or print them.
        return {"ok": False, "latency_seconds": elapsed, "status_code": exc.code, "error": "http_error"}
    except urllib.error.URLError as exc:
        elapsed = time.perf_counter() - started
        reason = exc.reason
        category = "timeout" if isinstance(reason, TimeoutError) else "connection_error"
        return {"ok": False, "latency_seconds": elapsed, "error": category}
    except TimeoutError:
        elapsed = time.perf_counter() - started
        return {"ok": False, "latency_seconds": elapsed, "error": "timeout"}
    except (json.JSONDecodeError, UnicodeDecodeError):
        elapsed = time.perf_counter() - started
        return {"ok": False, "latency_seconds": elapsed, "error": "invalid_json"}
    except OSError:
        elapsed = time.perf_counter() - started
        return {"ok": False, "latency_seconds": elapsed, "error": "network_error"}


def _nonnegative_number(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        return None
    return value
