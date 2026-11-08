from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

import api_server


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("DUCKAI_API_TOKEN", "client-secret")
    monkeypatch.setenv("UPSTREAM_BASE_URL", "https://provider.example/v1")
    monkeypatch.setenv("UPSTREAM_API_KEY", "provider-secret")
    return TestClient(api_server.app)


def install_mock_upstream(monkeypatch: pytest.MonkeyPatch, handler):
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        api_server,
        "make_http_client",
        lambda streaming=False: httpx.AsyncClient(
            transport=transport,
            timeout=httpx.Timeout(30.0),
            follow_redirects=False,
        ),
    )


def test_health_reports_proxy_configuration(client: TestClient) -> None:
    result = client.get("/health").json()
    assert result == {
        "status": "ok",
        "mode": "openai-proxy",
        "upstream_configured": True,
    }


def test_models_forward_without_authorization_when_upstream_key_is_absent(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("UPSTREAM_API_KEY", raising=False)

    async def handler(request: httpx.Request) -> httpx.Response:
        assert "authorization" not in request.headers
        return httpx.Response(200, json={"object": "list", "data": [{"id": "free-model"}]})

    install_mock_upstream(monkeypatch, handler)
    response = client.get("/v1/models", headers={"Authorization": "Bearer client-secret"})
    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == "free-model"


def test_health_reports_configured_when_upstream_key_is_optional(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("UPSTREAM_API_KEY", raising=False)
    assert client.get("/health").json()["upstream_configured"] is True


def test_models_forward_to_upstream_with_server_side_key(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://provider.example/v1/models"
        assert request.headers["authorization"] == "Bearer provider-secret"
        return httpx.Response(200, json={"object": "list", "data": [{"id": "real-model"}]})

    install_mock_upstream(monkeypatch, handler)
    response = client.get("/v1/models", headers={"Authorization": "Bearer client-secret"})
    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == "real-model"


def test_chat_completion_forwards_request_and_response(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer provider-secret"
        assert request.url.path == "/v1/chat/completions"
        assert request.read() == b'{"model":"real-model","messages":[{"role":"user","content":"hi"}]}'
        return httpx.Response(
            200,
            json={"id": "chatcmpl-real", "choices": [{"message": {"content": "hello from upstream"}}]},
        )

    install_mock_upstream(monkeypatch, handler)
    body = {"model": "real-model", "messages": [{"role": "user", "content": "hi"}]}
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer client-secret"},
        json=body,
    )
    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "hello from upstream"


def test_streaming_response_is_passed_through(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    sse = b'data: {"choices":[{"delta":{"content":"hello"}}]}\n\ndata: [DONE]\n\n'

    async def handler(request: httpx.Request) -> httpx.Response:
        assert b'"stream":true' in request.read()
        return httpx.Response(200, content=sse, headers={"content-type": "text/event-stream"})

    install_mock_upstream(monkeypatch, handler)
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer client-secret"},
        json={"model": "real-model", "messages": [], "stream": True},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.content == sse


def test_authentication_is_required(client: TestClient) -> None:
    response = client.get("/v1/models")
    assert response.status_code == 401


def test_upstream_http_errors_are_preserved(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": {"message": "rate limited"}})

    install_mock_upstream(monkeypatch, handler)
    response = client.get("/v1/models", headers={"Authorization": "Bearer client-secret"})
    assert response.status_code == 429
    assert response.json()["error"]["message"] == "rate limited"
