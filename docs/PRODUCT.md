# Product brief

## Vision

Make remote large-model inference measurable and comparable from a small computer, without downloading model weights or installing a machine-learning runtime.

## Problem

A model label such as “1T parameters” does not tell an engineer how a hosted endpoint behaves in their application. Results depend on serving infrastructure, queueing, network location, prompt length, generation settings, and provider limits. Today, developers often compare providers with ad hoc scripts that do not record their settings or failures consistently.

## Users

- **Open-source model evaluators** who need repeatable measurements for hosted model endpoints.
- **Application developers** deciding whether an endpoint meets latency and throughput needs.
- **Inference providers and maintainers** validating OpenAI-compatible API behavior.
- **Researchers and community members** documenting measurements with enough context to interpret them.

## Product promise

TrillionMoE Cloud Bench runs a small, explicit workload against a remote API and emits a transparent report. It does not claim to measure internal model compute or rank models independently of the test conditions.

## First release: v0.1

The first release is a Python CLI that:

1. Sends repeated chat-completion requests to one OpenAI-compatible remote endpoint.
2. Supports bounded concurrency and an optional warm-up count.
3. Captures client-observed latency, success/failure counts, HTTP status, and provider-reported token usage when available.
4. Calculates mean, p50/p95, successful requests per second, and output tokens per second.
5. Prints a concise terminal summary and can save a JSON report.
6. Reads credentials only from the named environment variable.
7. Never stores prompts, completions, or API keys in its report.

## Explicit non-goals

- Training, hosting, downloading, quantizing, or locally running a trillion-parameter model.
- Claiming that parameter count alone predicts quality, cost, or speed.
- Generating a universal leaderboard from incomparable runs.
- Sending traffic without an explicit user command.
- Hiding provider cost, rate-limit, or data-retention considerations.
- Collecting telemetry or uploading benchmark results automatically.
- Managing provider accounts, credentials, or billing.

## Success criteria

- A new contributor can install the CLI and see its help without a GPU or ML framework.
- A user can run a small, bounded benchmark against an OpenAI-compatible endpoint.
- The report includes enough run metadata to interpret the measurements.
- Failure cases are visible and do not silently become “slow” successful requests.
- Documentation clearly distinguishes client-side measurements from model-internal performance.
- Credentials, prompts, and generated text are not written to reports.

## Product principles

1. **Cloud inference, lightweight client.** Keep local dependencies small and do not fetch model weights.
2. **Explicit workload.** Make request count, concurrency, timeout, prompt, and generation settings visible.
3. **Honest measurements.** Report conditions and limitations alongside numbers.
4. **Privacy by default.** No telemetry; keep request content out of saved results.
5. **Provider-neutral core.** Start with the common OpenAI chat-completions shape; add adapters only with documented evidence.
6. **Safe defaults.** Small request counts and concurrency by default; no automatic retries that distort latency or multiply charges.
