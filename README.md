# TrillionMoE Cloud Bench

**Measure remote large-model inference from a lightweight client.**

TrillionMoE Cloud Bench is an open-source Python CLI for running bounded, repeatable benchmarks against remote OpenAI-compatible inference APIs. It records latency, throughput, provider-reported token usage, and failures without downloading or running model weights.

> **A trillion-parameter model is not running on your laptop.** This project measures a model served by a cloud provider. Your computer sends small HTTPS requests; inference stays on the provider's infrastructure.

[Product brief](docs/PRODUCT.md) · [Architecture](docs/ARCHITECTURE.md) · [Roadmap](docs/ROADMAP.md) · [Benchmark methodology](docs/BENCHMARKING.md) · [Contributing](CONTRIBUTING.md)

## Why this project

“1T parameters” describes a model, not the service experience a developer gets. Endpoint latency and throughput also depend on provider hardware, batching, queueing, network location, prompt length, and generation settings. This tool captures the workload and client-observed results in a portable JSON report so engineers can make more grounded comparisons.

## What it does

- Calls the common OpenAI chat-completions API shape
- Runs a requested number of calls with explicitly bounded concurrency
- Supports optional warm-up requests
- Reports success/failure totals, mean/p50/p95 latency, requests per second, and output tokens per second when the provider returns usage
- Saves a versioned JSON report on request
- Reads API keys from a named environment variable and omits prompts/completions from reports
- Uses Python's standard library at runtime; no GPU or ML stack is needed

## What it does not do

It does not train, host, download, quantize, or locally run trillion-parameter models. It does not measure server-side GPU utilization or isolated model compute. It does not retry failures automatically, upload reports, or call a provider until you run the command yourself.

## Install

Requires Python 3.10 or newer.

```bash
python -m pip install .
```

Set the environment variable used by your provider:

```powershell
# PowerShell
$env:TRILLION_BENCH_API_KEY = "your-provider-key"
```

```bash
# macOS / Linux
export TRILLION_BENCH_API_KEY="your-provider-key"
```

## Run a small benchmark

```bash
trillion-bench run \
  --base-url https://your-provider.example/v1 \
  --model your-model-id \
  --requests 5 \
  --concurrency 1 \
  --warmup 0 \
  --max-tokens 128 \
  --api-key-env TRILLION_BENCH_API_KEY \
  --output results.json
```

The endpoint URL must use HTTPS, except for localhost testing. Start with low request counts and concurrency. Requests and warm-ups may incur provider charges and may be subject to rate limits.

For full options:

```bash
trillion-bench run --help
```

## How to read results

Latency is end-to-end time observed by the client. It includes network transit, provider queueing, generation, and response transfer. Percentiles use nearest rank over successful samples. Output tokens per second is reported only when the endpoint returns token usage.

Results are meaningful only alongside their conditions. Keep provider region, model revision, prompt, generation settings, concurrency, warm-up policy, and client network location aligned. See [benchmark methodology](docs/BENCHMARKING.md) before publishing comparisons.

## Project status

The project is in active early development. The current milestone is a reliable single-endpoint benchmark CLI and documented report schema. Provider profiles, CSV export, report comparison, streaming metrics, and a static report viewer are planned; see the [roadmap](docs/ROADMAP.md).

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and open an issue for larger changes. CI never calls a paid live inference endpoint.

## License

MIT. See [LICENSE](LICENSE).
