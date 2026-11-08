# Temporary OpenAI-compatible proxy on GitHub Actions

This workflow exposes an authenticated OpenAI-compatible API through a temporary Cloudflare Tunnel. It forwards requests to an upstream provider; it does not generate mock answers or connect to Duck.ai's private browser interface.

## One-time setup

In **Settings → Secrets and variables → Actions**, add these repository secrets:

- `DUCKAI_API_TOKEN` — choose a long random token. This is the token you enter in Hermes (or another client) to access this proxy.
- `UPSTREAM_API_KEY` — the API key issued by the real provider you want the proxy to call. Keep it secret; it is sent only from the Runner to that provider.

## Start a session

1. Open **Actions → Temporary Runner API Test → Run workflow**.
2. Set `upstream_base_url` to your provider's OpenAI-compatible API base URL, usually ending in `/v1` (for example, `https://api.openai.com/v1`).
3. Set `tunnel_minutes` and run the workflow.
4. Copy `TEMPORARY_API_URL` from the job summary.

The selected upstream base URL and `UPSTREAM_API_KEY` must belong to the same provider/account. The key is never requested as a workflow input and is never returned to the client.

## Connect Hermes

Use the following values in Hermes:

- **Base URL:** `TEMPORARY_API_URL` followed by `/v1`
- **API Token / API Key:** the value stored in `DUCKAI_API_TOKEN`
- **Model:** choose one of the model IDs returned by `GET /v1/models`

The proxy forwards `GET /v1/models` and `POST /v1/chat/completions` to the selected upstream, including streaming requests. Model IDs and actual model availability depend on the upstream provider/account.

## Endpoints

- `GET /health` — public liveness/configuration check; does not reveal secrets or the upstream URL
- `GET /v1/models` — authenticated; returns the upstream provider's model list
- `POST /v1/chat/completions` — authenticated; forwards the request and response, including SSE streaming

Only HTTPS upstream base URLs are accepted so the upstream API key is not sent over plaintext HTTP. The temporary URL stops working when the workflow ends; GitHub-hosted runners are disposable, so each new session gets a new URL.

This workflow is manual-only (`workflow_dispatch`). Updating the code does not restart or modify an already-running session; start a new workflow run after the changes are merged.
