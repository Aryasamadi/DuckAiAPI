# Temporary OpenAI-compatible proxy on GitHub Actions

This workflow exposes an authenticated OpenAI-compatible API through a temporary Cloudflare Tunnel. It forwards requests to an OpenAI-compatible upstream endpoint.

## One-time setup

In **Settings → Secrets and variables → Actions**, add:

- `DUCKAI_API_TOKEN` — choose a long random token. This is the token you enter in Hermes (or another client) to access this proxy.
- `UPSTREAM_API_KEY` — optional. Add it only if the upstream provider requires authentication. Leave this secret absent for keyless upstream endpoints; GitHub does not accept empty secrets.

## Start a session

1. Open **Actions → Temporary Runner API Test → Run workflow**.
2. Set `upstream_base_url` to the HTTPS OpenAI-compatible API base URL, usually ending in `/v1`.
3. Set `tunnel_minutes` and run the workflow.
4. Copy `TEMPORARY_API_URL` from the job summary.

When `UPSTREAM_API_KEY` is present, the proxy sends it as a Bearer token to the upstream. When it is absent or empty, the Authorization header is omitted.

## Connect Hermes

- **Base URL:** `TEMPORARY_API_URL` followed by `/v1`
- **API Token / API Key:** the value stored in `DUCKAI_API_TOKEN`
- **Model:** choose a model ID returned by `GET /v1/models`

## Endpoints

- `GET /health` — public liveness/configuration check
- `GET /v1/models` — authenticated; forwards to upstream `/models`
- `POST /v1/chat/completions` — authenticated; forwards JSON and SSE streaming

Only HTTPS upstream URLs are accepted. This code supports keyless OpenAI-compatible endpoints, but it does not implement Duck.ai's private browser interface or prove that Duck.ai exposes a public OpenAI-compatible endpoint. The upstream URL must actually provide the endpoints above.

The workflow is manual-only (`workflow_dispatch`). Merging code does not restart or modify an already-running session; start a new workflow run to use the updated code.
