#!/usr/bin/env python3
"""Authenticated OpenAI-compatible API adapter for Duck.ai's existing client."""
from __future__ import annotations

import hmac
import json
import os
import threading
import time
import uuid
from typing import Any, Iterator

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI(title="Duck.ai OpenAI-Compatible API", version="2.1.0")

# Keep one Duck.ai HTTP session for the lifetime of this API process. The
# upstream client is stateful: it retains cookies, frontend version and VQD
# proof between turns. Recreating it for every OpenAI request causes repeated
# challenge/bootstrap traffic and can amplify upstream rate limits.
_DUCK_CLIENT: Any | None = None
_DUCK_CLIENT_LOCK = threading.Lock()
_DUCK_OPERATION_LOCK = threading.Lock()
_DUCK_RATE_LIMIT_LOCK = threading.Lock()
_DUCK_RATE_LIMIT_UNTIL = 0.0
_DUCK_RATE_LIMIT_DEFAULT_SECONDS = 60


def require_api_token(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    expected = os.environ.get("DUCKAI_API_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Proxy client token is not configured")
    supplied = x_api_key or ""
    if authorization and authorization.lower().startswith("bearer "):
        supplied = authorization[7:].strip()
    if not supplied or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API token")


def duckai_mode() -> bool:
    return os.environ.get("DUCKAI_MODE", "").strip().lower() in {"1", "true", "yes", "on"}


def configured() -> bool:
    return bool(os.environ.get("DUCKAI_API_TOKEN", "").strip()) and (
        duckai_mode() or bool(os.environ.get("UPSTREAM_BASE_URL", "").strip())
    )


def _text_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") in {"text", "input_text"}:
                value = item.get("text")
                if isinstance(value, str):
                    parts.append(value)
        return "\n".join(parts)
    return ""


def _duck_messages(messages: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    if not messages:
        raise HTTPException(status_code=400, detail="messages must contain at least one message")
    last_user = next((i for i in range(len(messages) - 1, -1, -1)
                      if messages[i].get("role") == "user"), None)
    if last_user is None:
        raise HTTPException(status_code=400, detail="messages must contain a user message")
    history = []
    for message in messages[:last_user]:
        role = message.get("role")
        if role not in {"system", "user", "assistant"}:
            continue
        text = _text_content(message.get("content"))
        if text:
            history.append({"role": role, "content": [{"type": "text", "text": text}]})
    prompt = _text_content(messages[last_user].get("content"))
    if not prompt:
        raise HTTPException(status_code=400, detail="The latest user message must contain text")
    return prompt, history


def _create_duck_client():
    # Lazy import keeps the generic upstream proxy independent from Duck.ai dependencies.
    try:
        from duck_cli import DuckAI
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Duck.ai adapter dependencies unavailable: {type(exc).__name__}") from exc
    return DuckAI()


def _duck_client():
    """Return the process-wide, stateful Duck.ai session."""
    global _DUCK_CLIENT
    if _DUCK_CLIENT is None:
        with _DUCK_CLIENT_LOCK:
            if _DUCK_CLIENT is None:
                _DUCK_CLIENT = _create_duck_client()
    return _DUCK_CLIENT


def _retry_after_seconds(value: Any = None) -> int:
    try:
        seconds = int(float(value))
    except (TypeError, ValueError, OverflowError):
        seconds = _DUCK_RATE_LIMIT_DEFAULT_SECONDS
    return max(1, min(seconds, 3600))


def _set_duck_rate_limit(retry_after: Any = None) -> int:
    global _DUCK_RATE_LIMIT_UNTIL
    seconds = _retry_after_seconds(retry_after)
    with _DUCK_RATE_LIMIT_LOCK:
        _DUCK_RATE_LIMIT_UNTIL = max(
            _DUCK_RATE_LIMIT_UNTIL, time.monotonic() + seconds
        )
        return max(1, int(_DUCK_RATE_LIMIT_UNTIL - time.monotonic() + 0.999))


def _check_duck_rate_limit() -> None:
    with _DUCK_RATE_LIMIT_LOCK:
        remaining = int(_DUCK_RATE_LIMIT_UNTIL - time.monotonic() + 0.999)
    if remaining > 0:
        raise HTTPException(
            status_code=429,
            detail=f"Duck.ai rate limit is active. Retry after {remaining} seconds.",
            headers={"Retry-After": str(remaining)},
        )


def _raise_duck_exception(exc: Exception) -> None:
    if getattr(exc, "status", None) == 429:
        retry_after = _set_duck_rate_limit(getattr(exc, "retry_after", None))
        raise HTTPException(
            status_code=429,
            detail=f"Duck.ai rate-limited the request. Retry after {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        ) from exc
    raise HTTPException(
        status_code=502,
        detail=f"Duck.ai request failed: {str(exc)[:800]}",
    ) from exc


def _prepare_duck_session(client: Any) -> None:
    """Perform the first handshake before returning streaming HTTP headers."""
    _check_duck_rate_limit()
    if not hasattr(client, "rehandshake"):
        return
    if getattr(client, "fe_version", "") and getattr(client, "jsa", ""):
        return
    try:
        client.rehandshake()
    except Exception as exc:
        _raise_duck_exception(exc)


def _duck_stream(prompt: str, model: str, history: list[dict[str, Any]], request_id: str,
                 created: int) -> Iterator[bytes]:
    client = _duck_client()
    with _DUCK_OPERATION_LOCK:
        try:
            _check_duck_rate_limit()
            for kind, value in client.stream_events(prompt, model=model, history=history):
                if kind != "message" or not value:
                    continue
                chunk = {
                    "id": request_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{"index": 0, "delta": {"content": value}, "finish_reason": None}],
                }
                yield ("data: " + json.dumps(chunk, ensure_ascii=False) + "\n\n").encode("utf-8")
            final_chunk = {
                "id": request_id, "object": "chat.completion.chunk", "created": created,
                "model": model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            yield ("data: " + json.dumps(final_chunk) + "\n\n").encode("utf-8")
            yield b"data: [DONE]\n\n"
        except Exception as exc:
            if getattr(exc, "status", None) == 429:
                retry_after = _set_duck_rate_limit(getattr(exc, "retry_after", None))
                message = f"Duck.ai rate-limited the request. Retry after {retry_after} seconds."
                error_type = "rate_limit_error"
            else:
                message = str(exc)[:1000]
                error_type = "duckai_error"
            error = {"error": {"message": message, "type": error_type}}
            yield ("data: " + json.dumps(error, ensure_ascii=False) + "\n\n").encode("utf-8")


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "mode": "duckai" if duckai_mode() else "openai-proxy",
        "upstream_configured": configured(),
    }


@app.get("/v1/models", dependencies=[Depends(require_api_token)])
async def list_models(request: Request):
    if duckai_mode():
        try:
            from duck_cli import MODELS
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Duck.ai adapter dependencies unavailable") from exc
        model_ids = sorted(set(MODELS.values()))
        return {"object": "list", "data": [
            {"id": model_id, "object": "model", "created": 0, "owned_by": "duck.ai"}
            for model_id in model_ids
        ]}
    return await forward_upstream("GET", "models", request)


async def forward_upstream(method: str, endpoint: str, request: Request, body: bytes | None = None):
    import httpx
    from urllib.parse import urlsplit

    base_url = os.environ.get("UPSTREAM_BASE_URL", "").strip().rstrip("/")
    upstream_key = os.environ.get("UPSTREAM_API_KEY", "").strip()
    parsed = urlsplit(base_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise HTTPException(status_code=503, detail="Set a valid HTTPS UPSTREAM_BASE_URL.")
    headers = {"Accept": request.headers.get("accept", "application/json")}
    if upstream_key:
        headers["Authorization"] = f"Bearer {upstream_key}"
    if body is not None:
        headers["Content-Type"] = request.headers.get("content-type", "application/json")
    timeout = httpx.Timeout(connect=20.0, read=None, write=60.0, pool=20.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
        response = await client.request(method, f"{base_url}/{endpoint}", params=request.query_params,
                                        headers=headers, content=body)
        return JSONResponse(content=response.json(), status_code=response.status_code,
                            headers={"Cache-Control": "no-store"})


@app.post("/v1/chat/completions", dependencies=[Depends(require_api_token)])
async def chat_completions(request: Request):
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("messages"), list):
        raise HTTPException(status_code=400, detail="Request must include a messages array")

    if not duckai_mode():
        raw_body = json.dumps(payload, separators=(",", ":")).encode()
        return await forward_upstream("POST", "chat/completions", request, raw_body)

    prompt, history = _duck_messages(payload["messages"])
    model = str(payload.get("model") or "gpt-6-luna")
    try:
        from duck_cli import MODELS
        model = MODELS.get(model, model)
        if model not in set(MODELS.values()):
            raise HTTPException(status_code=400, detail=f"Unknown Duck.ai model: {model}")
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="Duck.ai adapter dependencies unavailable") from exc

    request_id = "chatcmpl-" + uuid.uuid4().hex
    created = int(time.time())
    client = _duck_client()
    if payload.get("stream") is True:
        # Fail before sending HTTP 200/SSE headers if the upstream challenge
        # endpoint is already rate-limiting this session.
        with _DUCK_OPERATION_LOCK:
            _prepare_duck_session(client)
        return StreamingResponse(
            _duck_stream(prompt, model, history, request_id, created),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
        )

    with _DUCK_OPERATION_LOCK:
        _prepare_duck_session(client)
        try:
            answer = client.ask(prompt, model=model, history=history)
        except Exception as exc:
            _raise_duck_exception(exc)
    return {
        "id": request_id,
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": answer},
            "finish_reason": "stop",
        }],
    }
