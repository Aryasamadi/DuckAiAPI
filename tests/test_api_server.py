from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import api_server


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("DUCKAI_API_TOKEN", "client-secret")
    monkeypatch.setenv("DUCKAI_MODE", "1")
    return TestClient(api_server.app)


def test_health_reports_duckai_mode(client: TestClient) -> None:
    assert client.get("/health").json() == {
        "status": "ok", "mode": "duckai", "upstream_configured": True
    }


def test_models_lists_duckai_models(client: TestClient) -> None:
    response = client.get("/v1/models", headers={"Authorization": "Bearer client-secret"})
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["data"]}
    assert "gpt-6-luna" in ids
    assert "gpt-5.4-mini" in ids


def test_chat_completion_uses_duckai_client(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeDuckAI:
        def ask(self, prompt, model, history):
            assert prompt == "hello"
            assert model == "gpt-5.4-mini"
            assert history == [\n                {"role": "user", "content": [{"type": "text", "text": "previous"}]},\n                {"role": "assistant", "content": [{"type": "text", "text": "old answer"}]},\n            ]
            return "hello from Duck.ai"

    monkeypatch.setattr(api_server, "_duck_client", lambda: FakeDuckAI())
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer client-secret"},
        json={"model": "mini", "messages": [
            {"role": "user", "content": "previous"},
            {"role": "assistant", "content": "old answer"},
            {"role": "user", "content": "hello"},
        ]},
    )
    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "hello from Duck.ai"


def test_chat_requires_authentication(client: TestClient) -> None:
    response = client.post("/v1/chat/completions", json={"messages": [{"role": "user", "content": "hi"}]})
    assert response.status_code == 401


def test_rejects_unknown_model(client: TestClient) -> None:
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer client-secret"},
        json={"model": "not-a-duck-model", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert response.status_code == 400


def test_streaming_chat_returns_openai_sse(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeDuckAI:
        def stream_events(self, prompt, model, history):
            assert prompt == "stream this"
            yield ("message", "hello ")
            yield ("message", "stream")

    monkeypatch.setattr(api_server, "_duck_client", lambda: FakeDuckAI())
    with client.stream(
        "POST",
        "/v1/chat/completions",
        headers={"Authorization": "Bearer client-secret"},
        json={"model": "luna", "stream": True, "messages": [{"role": "user", "content": "stream this"}]},
    ) as response:
        body = "".join(response.iter_text())
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert '"content": "hello "' in body
    assert '"content": "stream"' in body
    assert "data: [DONE]" in body
