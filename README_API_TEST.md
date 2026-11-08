# Temporary GitHub Runner API test

This adds a temporary OpenAI-compatible HTTP surface for validating the API
contract, bearer-token authentication, streaming responses, and GitHub-hosted
runner/tunnel lifecycle.

**Important:** this is deliberately a mock backend. It does not send requests
to Duck.ai or reproduce Duck.ai's private anti-abuse/browser challenge flow.
Responses begin with `[MOCK MODE]`.

## One-time setup

1. Open repository **Settings → Secrets and variables → Actions**.
2. Add repository secret `DUCKAI_API_TOKEN` with a long random token you choose.
3. Do not put the token in source code or workflow YAML.

The same secret is used on every workflow run, so your API token remains stable.

## Start a test session

1. Open **Actions → Temporary Runner API Test**.
2. Choose **Run workflow** and set `tunnel_minutes` (1–350).
3. When the job starts, open its summary and copy `TEMPORARY_API_URL`.

The URL is temporary and stops working when the workflow ends. GitHub-hosted
runners are disposable; start a new workflow to get a new URL.

## Test

Set `BASE_URL` to the URL shown in the workflow summary and use your secret:

```bash
curl "$BASE_URL/health"

curl "$BASE_URL/v1/models" \
  -H "Authorization: Bearer $DUCKAI_API_TOKEN"

curl "$BASE_URL/v1/chat/completions" \
  -H "Authorization: Bearer $DUCKAI_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-6-luna",
    "messages": [{"role": "user", "content": "hello"}]
  }'
```

Streaming is available with `"stream": true` and returns Server-Sent Events.

## Endpoints

- `GET /health` — public liveness check (no token)
- `GET /v1/models` — requires bearer token or `X-API-Key`
- `POST /v1/chat/completions` — requires bearer token or `X-API-Key`

This workflow is manual-only (`workflow_dispatch`); pushes and pull requests do
not start a runner. It does not restart or modify any external runner.
