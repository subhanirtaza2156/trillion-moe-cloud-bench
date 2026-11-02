# Roadmap

This roadmap describes direction, not a promise of dates. Work should be tracked in GitHub issues with acceptance criteria and provider evidence.

## v0.2 — Reliable single-endpoint runs (current)

- [x] OpenAI-compatible chat-completions request
- [x] Human-readable output and versioned JSON report
- [x] Bounded concurrency and explicit warm-ups
- [x] Input validation and actionable, sanitized error categories
- [x] CI package-install and CLI smoke check (no live provider calls)
- [x] Methodology, cost, security, and data-handling docs
- [x] Report schema and provider-compatibility policy

## v0.3 — Repeatable experiments

- [ ] Provider profile format with secret values kept in environment variables
- [ ] Optional CSV export
- [ ] Report comparison with workload compatibility checks
- [ ] Run metadata: client version and generation settings in reports
- [ ] Redaction review and report-schema compatibility policy

## v0.4 — Provider compatibility

- [ ] Adapter interface and documented provider compatibility matrix
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
