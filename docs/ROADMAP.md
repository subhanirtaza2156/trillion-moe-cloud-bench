# Roadmap

This roadmap describes direction, not a promise of dates. Work should be tracked in GitHub issues with acceptance criteria and provider evidence.

## v0.1 — Reliable single-endpoint runs

- [x] OpenAI-compatible chat-completions request
- [x] Human-readable output and versioned JSON report
- [ ] Bounded concurrency and explicit warm-ups
- [ ] Input validation and actionable error categories
- [ ] CI install/CLI smoke check
- [ ] Clear docs for methodology, cost, and data handling

## v0.2 — Repeatable experiments

- [ ] Provider profile format with secret values kept in environment variables
- [ ] Optional CSV export
- [ ] Run metadata: client version, OS/Python version, concurrency, warm-ups, generation settings
- [ ] Compare two reports only when workload settings are compatible
- [ ] Redaction and report-schema documentation

## v0.3 — Provider compatibility

- [ ] Adapter interface and provider compatibility matrix
- [ ] Streaming measurements including first-token and inter-token timing
- [ ] Provider-specific request/response variations backed by docs or reproducible examples
- [ ] Clear indication when metrics cannot be compared

## v1.0 — Stable benchmark format

- [ ] Stable report schema and migration policy
- [ ] Reproducible scenario files
- [ ] Optional offline report viewer; no automatic uploads
- [ ] Security and compatibility review
- [ ] Community-maintained provider adapters and contribution guide

## Not planned without a demonstrated need

- Local model loading or weight downloads
- A hosted service that collects users' prompts or credentials
- Unbounded load generation
- A “best model” ranking that ignores workload and serving conditions
- Automatic publication of results
