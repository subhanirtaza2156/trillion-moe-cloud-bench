# JSON report schema v1

The `--output` option writes one JSON object. Schema changes that break consumers require a new `schema_version`.

## Top-level fields

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | integer | Current report contract version; currently `1`. |
| `started_at` | string | UTC timestamp at the start of measured requests (warm-ups excluded). |
| `endpoint` | string | Endpoint scheme, host, and path; query and fragment are omitted. |
| `model` | string | Model identifier supplied to the endpoint. |
| `workload` | object | Measured request count, max concurrency, warm-up count. |
| `environment` | object | Python version and operating system name. |
| `summary` | object | Aggregate outcomes and metrics. |
| `samples` | array | One outcome record per measured request, ordered by request index. |

## Summary fields

`success_count` and `failure_count` count measured calls only. `wall_time_seconds` covers the measured batch and excludes warm-ups. `latency_seconds.mean`, `p50`, and `p95` use successful samples and nearest-rank percentiles. Requests per second is successful requests divided by batch wall time.

Token totals and output tokens per second are `null` when the endpoint does not return usable token usage. Missing usage is not treated as zero.

## Sample fields

A sample includes `request_index`, `ok`, and `latency_seconds`; it may include `status_code`, `prompt_tokens`, `completion_tokens`, or a short `error` category. It never contains the prompt, completion text, authorization header, or full provider response body.

## Compatibility

Consumers should check `schema_version` and tolerate absent or null optional metrics. A future breaking shape change will increment the version and be documented here.
