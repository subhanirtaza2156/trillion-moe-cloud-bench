# TrillionMoE Cloud Bench

A lightweight benchmark CLI for **remote, OpenAI-compatible inference APIs**. Compare latency, throughput, token usage, and failures across hosted large-model endpoints, including Mixture-of-Experts services.

> This project does not train, download, or run trillion-parameter weights. Your computer sends small HTTPS requests to a provider endpoint; model inference happens on the provider's infrastructure.

## Features

- Uses Python's standard library; no heavy ML dependencies
- Sends repeated chat-completion requests to an OpenAI-compatible endpoint
- Reports successful requests, failures, average and p50/p95 latency, requests/second, and output tokens/second when usage data is returned
- Can save machine-readable JSON results
- Reads API credentials from an environment variable; never writes them to disk

## Requirements

- Python 3.10+
- An OpenAI-compatible remote inference endpoint and a model ID
- Network access to that endpoint

## Quickstart

Install from a checkout:

```bash
python -m pip install .
```

Set your provider key in the environment (replace the variable name/value for your provider):

```bash
# PowerShell
$env:TRILLION_BENCH_API_KEY = "your-provider-key"

# macOS / Linux
export TRILLION_BENCH_API_KEY="your-provider-key"
```

Run a small benchmark:

```bash
trillion-bench run \
  --base-url https://your-provider.example/v1 \
  --model your-model-id \
  --prompt "Explain mixture-of-experts inference in one paragraph." \
  --requests 5 \
  --api-key-env TRILLION_BENCH_API_KEY \
  --output results.json
```

You can also run it without installing:

```bash
python -m trillion_moe_cloud_bench run --base-url https://your-provider.example/v1 --model your-model-id
```

The CLI defaults to 5 requests and a short sample prompt. Start with a low request count and respect the provider's rate limits and billing terms. The tool makes real requests and may incur provider charges.

## Output metrics

- **Latency:** client-observed end-to-end request duration
- **p50 / p95:** nearest-rank latency percentiles over successful requests
- **Requests/sec:** successful requests divided by total benchmark wall time
- **Output tokens/sec:** reported completion tokens divided by total benchmark wall time; omitted when the provider does not return usage data

These are client-side measurements, not claims about a model's internal compute speed. Network conditions, provider queues, caching, generation length, and rate limits affect results. Compare runs only when prompts, generation settings, region, and provider conditions are similar.

## Provider compatibility

The first version calls `POST {base-url}/chat/completions` and expects the common OpenAI chat-completions response shape. Providers may differ in URL format, authentication, or usage reporting. Check your provider's API docs before running.

## Development

```bash
python -m pip install -e .
python -m trillion_moe_cloud_bench --help
```

Contributions are welcome. Please open an issue with the provider/API shape and a redacted example response when reporting compatibility problems. Never include API keys or private prompts in issues.

## License

MIT. See [LICENSE](LICENSE).
