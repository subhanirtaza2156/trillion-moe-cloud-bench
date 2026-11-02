# Contributing

Thanks for helping improve TrillionMoE Cloud Bench. Contributions should make remote inference measurements safer, clearer, or more reproducible.

## Before opening a pull request

1. Search existing issues and discussions for related work.
2. For a substantial change, open an issue describing the user problem and proposed behavior.
3. Keep pull requests focused; update the product or methodology docs when behavior changes.
4. Never include API keys, real user prompts, generated private content, or unredacted provider traces.

## Development setup

- Python 3.10 or newer
- Install editable package: `python -m pip install -e .`
- Check command help: `python -m trillion_moe_cloud_bench --help`

Do not run a real endpoint benchmark in CI. Live API calls can incur charges, depend on provider availability, and expose test prompts to a third party.

## Engineering expectations

- Keep core dependencies small and avoid ML runtimes or model-weight downloads.
- Bound concurrency and avoid implicit retries.
- Keep credentials out of arguments, logs, reports, and example files.
- Preserve the report schema or document a version change.
- Make unavailable provider metrics explicit rather than substituting zero.
- Document the exact API behavior and test conditions for provider-specific support.
- Include tests for code changes in pull requests; use mocked HTTP responses, not paid live endpoints.

## Pull request checklist

- [ ] The change solves a documented user need.
- [ ] Documentation and CLI help match the implementation.
- [ ] No secrets or private prompts are included.
- [ ] Provider calls are bounded and explicit.
- [ ] Report fields remain privacy-conscious and versioned.
