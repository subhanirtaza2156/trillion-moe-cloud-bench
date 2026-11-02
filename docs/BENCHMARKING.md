# Benchmark methodology

## What is measured

The client measures elapsed wall-clock time around each HTTP request. That includes client networking, provider queueing, generation, and response transfer. It is an end-to-end observation from the machine running the CLI.

When an endpoint returns token usage, the report includes total prompt and completion tokens and derives output tokens per second from total completion tokens divided by the benchmark wall time.

## What is not measured

The tool does not measure GPU utilization, model FLOPs, internal time-to-first-token, server-side queue time, energy, or isolated model compute. It cannot infer those values from a standard non-streaming response.

## Making comparisons useful

For each comparison, keep the following conditions aligned:

- provider region and client network location
- exact model identifier and provider revision, when exposed
- prompt text and generation limit
- request count, concurrency, temperature, and timeout
- warm-up policy
- time window, provider load, and account tier

Run multiple sessions if the result matters. Record provider/model changes and interpret variance rather than selecting a single best run.

## Concurrency and provider limits

Concurrency is bounded by an explicit CLI setting. Higher concurrency can trigger queueing, throttling, or billing. Start low, use only endpoints you are authorized to benchmark, and follow provider limits. The tool does not retry failed requests automatically.

## Percentiles and small samples

Percentiles use the nearest-rank method over successful samples. Small runs produce unstable p95 values; use a larger request count only when the endpoint terms and budget allow it.

## Report privacy

JSON reports include endpoint host/path and aggregate/sample metadata. They exclude the prompt, model output, and authorization token. Review reports before sharing because endpoint names or model IDs may still be sensitive in your context.
