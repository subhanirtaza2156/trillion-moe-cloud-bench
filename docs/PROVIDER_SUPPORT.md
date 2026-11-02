# Provider support

## Current contract

The initial client targets the common OpenAI-compatible chat-completions API:

- Request: `POST {base-url}/chat/completions`
- Authentication: optional bearer token from a user-selected environment variable
- Response: JSON object; token metrics read from `usage.prompt_tokens` and `usage.completion_tokens` when present

Use the base URL expected by your provider, commonly including its API prefix such as `/v1`. The tool does not discover model IDs or verify account access before running.

## Current limits

The first release sends one user message and uses `max_tokens` and `temperature`. It does not yet support streaming, provider-specific headers, alternate token limit fields, multi-turn scenarios, or automatic retries. Some providers may accept the request but omit usage metrics. A successful HTTP response is not a quality evaluation.

## Adding a provider

Before adding a provider adapter:

1. Link the provider's public API documentation.
2. Describe URL, authentication, request, response, and usage-field differences.
3. Provide redacted example payloads that contain no real user prompt, output, token, or account identifier.
4. Preserve the shared report semantics or explain what is unavailable.
5. Add a compatibility entry here and make the default traffic limits explicit.

Do not add provider credentials to profiles or checked-in examples. Keep secrets in environment variables.
