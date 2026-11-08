# Temporary Duck.ai API for Hermes

This workflow exposes the existing DuckAi Python client through an authenticated OpenAI-compatible API and a temporary Cloudflare Tunnel. It is intended for personal testing.

## One-time setup

In **Settings → Secrets and variables → Actions**, add:

- `DUCKAI_API_TOKEN` — choose a long random token. Enter this same value in Hermes.

No `UPSTREAM_API_KEY` or upstream Base URL is needed in Duck.ai mode.

## Start a session

1. Open **Actions → Temporary Runner API Test → Run workflow**.
2. Choose how many minutes to keep the temporary endpoint alive.
3. Run the workflow and wait for the tunnel step.
4. Copy `TEMPORARY_API_URL` from the job summary.

## Hermes configuration

- **Base URL:** `TEMPORARY_API_URL/v1`
- **API Token / API Key:** your `DUCKAI_API_TOKEN`
- **Model:** choose an ID returned by `GET /v1/models`, such as `gpt-6-luna` or `gpt-5.4-mini`.

## Supported endpoints

- `GET /health` — mode and configuration status
- `GET /v1/models` — Duck.ai model list
- `POST /v1/chat/completions` — normal and SSE streaming chat completions

The adapter translates OpenAI-style chat messages to the existing `DuckAI` client in `duck_cli.py`. The client needs Python dependencies, Node.js 20, and `jsdom` to perform its current Duck.ai session bootstrap. Image input and tool calls are not exposed by this first API adapter; text chat and streaming are the test target.

The workflow is manual-only. Starting a new workflow creates a new temporary tunnel; it does not restart or stop any other runner session.
