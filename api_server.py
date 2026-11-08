#!/usr/bin/env python3
"""OpenAI-compatible test API for validating the GitHub Actions runner setup.

This server intentionally uses a deterministic mock response. It does not call
Duck.ai or replay its private browser/challenge protocol.
"""
from __future__ import annotations

import hmac
import json
import os
import time
import uuid
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

API_TOKEN = os.environ.get("DUCKAI_API_TOKEN", "")
if not API_TOKEN:
    raise RuntimeError("DUCKAI_API_TOKEN is required")

app = FastAPI(title="DuckAiAPI Runner Test", version="0.1.0")


def require_api_token(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    supplied = x_api_key or ""
    if authorization and authorization.lower().startswith("bearer "):
        supplied = authorization[7:].strip()
    if not supplied or not hmac.compare_digest(supplied, API_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid or missing API token")


class ChatRequest(BaseModel):
    model: str = "gpt-6-luna"
    messages: list[dict[str, Any]] = Field(default_factory=list)
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "mock", "service": "DuckAiAPI Runner Test"}


@app.get("/v1/models", dependencies=[Depends(require_api_token)])
def models() -> dict[str, Any]:
    return {
        "object": "list",
        "data": [
            {"id": "gpt-6-luna", "object": "model", "owned_by": "duckai-test"},
            {"id": "gpt-5.4-mini", "object": "model", "owned_by": "duckai-test"},
            {"id": "claude-haiku-5-5", "object": "model", "owned_by": "duckai-test"},
        ],
    }


def last_user_message(messages: list[dict[str, Any]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            content = message.get("content", "")
            if isinstance(content, str):
                return content
            return json.dumps(content, ensure_ascii=False)
    return ""


@app.post("/v1/chat/completions", dependencies=[Depends(require_api_token)])
def chat_completions(request: ChatRequest):
    prompt = last_user_message(request.messages)
    answer = (
        "[MOCK MODE] Runner API authentication and request handling are working. "
        f"Received: {prompt[:500]}"
    )
    completion_id = "chatcmpl-" + uuid.uuid4().hex

    if request.stream:
        def events():
            chunks = [answer[i:i + 32] for i in range(0, len(answer), 32)]
            for chunk in chunks:
                payload = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": request.model,
                    "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}],
                }
                yield "data: " + json.dumps(payload, ensure_ascii=False) + "\n\n"
            final_payload = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            yield "data: " + json.dumps(final_payload) + "\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": answer},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
