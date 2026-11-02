# Architecture

## Current system

The initial release is a single-user command-line program with three boundaries:

- **CLI and validation** parse endpoint, model, workload, timeout, and output options.
- **HTTP client** sends one JSON chat-completions request per sample and returns status, duration, and provider-reported usage. It does not retain response text.
- **Aggregator and renderers** calculate summary metrics, print a terminal summary, and optionally serialize a versioned JSON report.

## Data flow

```text
CLI arguments + named environment variable
                 |
                 v
       validate bounded workload
                 |
                 v
  concurrent HTTPS requests to provider
                 |
                 v
 status + duration + usage metadata only
                 |
           +-----+-----+
           v           v
     CLI summary   local JSON report
```

The program sends data only after the user runs the benchmark command. There is no background process, account sign-in, telemetry, or automatic upload.

## Request contract

The initial adapter posts to `{base-url}/chat/completions` using:

- `model`
- one user message
- `max_tokens`
- `temperature`

The response adapter reads the common `usage.prompt_tokens` and `usage.completion_tokens` fields. Missing usage is represented as unavailable, not zero. Provider-specific response bodies are not printed or stored.

## Report contract

JSON reports use a `schema_version` field so future additions can be versioned. Each sample contains an outcome, latency, status code when available, token counts when available, and a sanitized error category. Reports intentionally omit the prompt, completion, authorization header, and full response body.

## Scaling the project

The implementation should grow in deliberate layers:

1. **Stable measurement core:** request/response adapters, workload validation, aggregation, report schema.
2. **Provider profiles:** documented endpoint/auth variations, without putting secret values in config files.
3. **Comparison workflows:** multiple saved reports with compatibility checks for workload settings.
4. **Optional dashboard:** only after the JSON schema stabilizes; static report viewing should remain local and opt-in.
5. **Distributed runs:** only if a concrete use case requires them; preserve bounded traffic and comparable run metadata.

## Design constraints

- Python standard library for the core runtime.
- No model frameworks or model-weight dependencies.
- Bounded worker count; never create one thread per request without a cap.
- No automatic retry by default, because retries alter latency and may incur charges.
- Keep the transport replaceable so async HTTP or provider adapters can be introduced without rewriting report aggregation.
- Keep all result formats explicit and documented.
