# Security policy

## Supported versions

Security fixes target the latest released version and the current default branch.

## Reporting a vulnerability

Please do not publish credentials, exploitable endpoint URLs, or sensitive request data in a public issue. Use GitHub's private vulnerability reporting for this repository when available. If it is unavailable, contact the repository owner through the private contact channel listed on their GitHub profile.

Include a concise impact description and reproduction steps with secrets and personal data removed. Do not send API keys or customer prompts.

## Data and credential handling

- API keys are read from an environment variable named by the user.
- The tool does not persist credentials, prompts, completions, or response bodies.
- Saved reports contain measurement metadata and sanitized error categories.
- Users should inspect endpoint/model metadata before sharing reports.
- Benchmark requests go to the user-selected third-party service and are subject to that service's terms and data handling.

## Scope

The project is a local CLI. It does not expose a listening server, run background tasks, or upload reports.
