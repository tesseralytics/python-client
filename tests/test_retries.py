"""Tests for retry/backoff behaviour."""

from __future__ import annotations

import httpx
import pytest
import respx

from tessera import AuthenticationError, ServiceUnavailableError, TesseraClient
from tessera.errors import NetworkError
from tests.conftest import BASE_URL


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tessera.client.time.sleep", lambda _seconds: None)


@respx.mock
def test_retries_503_then_succeeds(api_key: str) -> None:
    route = respx.get(f"{BASE_URL}/v1/datasets").mock(
        side_effect=[
            httpx.Response(503, json={"error": "unavailable"}),
            httpx.Response(200, json={"generated_at": "t", "datasets": []}),
        ]
    )
    with TesseraClient(max_retries=2) as client:
        resp = client.datasets()
    assert resp.datasets == []
    assert route.call_count == 2


@respx.mock
def test_gives_up_after_max_retries(api_key: str) -> None:
    route = respx.get(f"{BASE_URL}/v1/datasets").mock(
        return_value=httpx.Response(503, json={"error": "unavailable"})
    )
    with TesseraClient(max_retries=2) as client, pytest.raises(ServiceUnavailableError):
        client.datasets()
    assert route.call_count == 3  # initial + 2 retries


@respx.mock
def test_does_not_retry_4xx(api_key: str) -> None:
    route = respx.get(f"{BASE_URL}/v1/datasets").mock(
        return_value=httpx.Response(401, json={"error": "unauthorized"})
    )
    with TesseraClient(max_retries=3) as client, pytest.raises(AuthenticationError):
        client.datasets()
    assert route.call_count == 1


@respx.mock
def test_network_error_wrapped(api_key: str) -> None:
    respx.get(f"{BASE_URL}/v1/datasets").mock(side_effect=httpx.ConnectError("boom"))
    with TesseraClient(max_retries=1) as client, pytest.raises(NetworkError):
        client.datasets()
