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
            assert history == [
                {"role": "user", "content": [{"type": "text", "text": "previous"}]},
                {"role": "assistant", "content": [{"type": "text", "text": "old answer"}]},
            ]
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


@pytest.fixture(autouse=True)
def reset_duckai_process_state(monkeypatch: pytest.MonkeyPatch) -> None:
    # Each test gets a clean process-wide session and rate-limit window.
    monkeypatch.setattr(api_server, "_DUCK_CLIENT", None)
    monkeypatch.setattr(api_server, "_DUCK_RATE_LIMIT_UNTIL", 0.0)


def test_duck_client_is_reused_for_the_process(monkeypatch: pytest.MonkeyPatch) -> None:
    created = object()
    calls = 0

    def factory():
        nonlocal calls
        calls += 1
        return created

    monkeypatch.setattr(api_server, "_create_duck_client", factory)

    assert api_server._duck_client() is created
    assert api_server._duck_client() is created
    assert calls == 1


def test_challenge_429_is_returned_and_suppresses_repeat_handshakes(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FakeRateLimitError(Exception):
        status = 429
        retry_after = "45"

    class FakeDuckAI:
        fe_version = ""
        jsa = ""

        def __init__(self):
            self.handshake_calls = 0

        def rehandshake(self):
            self.handshake_calls += 1
            raise FakeRateLimitError("No challenge received (HTTP 429)")

        def ask(self, prompt, model, history):
            raise AssertionError("ask must not run when the challenge is rate-limited")

    fake = FakeDuckAI()
    monkeypatch.setattr(api_server, "_duck_client", lambda: fake)
    request = {
        "model": "mini",
        "messages": [{"role": "user", "content": "hello"}],
    }
    headers = {"Authorization": "Bearer client-secret"}

    first = client.post("/v1/chat/completions", headers=headers, json=request)
    second = client.post("/v1/chat/completions", headers=headers, json=request)

    assert first.status_code == 429
    assert first.headers["retry-after"] == "45"
    assert second.status_code == 429
    assert fake.handshake_calls == 1


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


def test_duck_client_does_not_retry_http_429(monkeypatch: pytest.MonkeyPatch) -> None:
    from duck_cli import DuckAI, DuckAIError

    class FakeResponse:
        status_code = 429
        headers = {"Retry-After": "12"}
        text = "rate limited"

        def close(self):
            pass

    client = DuckAI()
    client.fe_version = "test-version"
    client.jsa = "test-proof"
    calls = 0

    def fake_chat(*args, **kwargs):
        nonlocal calls
        calls += 1
        return FakeResponse()

    monkeypatch.setattr(client, "chat", fake_chat)

    with pytest.raises(DuckAIError) as exc_info:
        list(client.stream_events("hello"))

    assert exc_info.value.status == 429
    assert exc_info.value.retry_after == "12"
    assert calls == 1
