"""Tests for the synchronous client's metadata endpoints, auth, and config."""

from __future__ import annotations

import httpx
import pytest
import respx

from tessera import ForbiddenError, NotFoundError, TesseraClient
from tessera.errors import ConfigurationError
from tests.conftest import API_KEY, BASE_URL

DATASETS_BODY = {
    "generated_at": "2025-09-27T10:30:00Z",
    "datasets": [
        {
            "name": "gold_ohlcv_1m",
            "partition_count": 2,
            "coins": ["BTC", "ETH"],
            "months": {"earliest": "2025-08", "latest": "2025-09"},
        }
    ],
}

PARTITIONS_BODY = {
    "asset": "gold_ohlcv_1m",
    "generated_at": "2025-09-27T10:30:00Z",
    "partitions": [
        {"coin": "BTC", "month": "2025-09", "size_bytes": 1024, "modified_at": None},
    ],
}


@respx.mock
def test_datasets(api_key: str) -> None:
    route = respx.get(f"{BASE_URL}/v1/datasets").mock(
        return_value=httpx.Response(200, json=DATASETS_BODY)
    )
    with TesseraClient() as client:
        resp = client.datasets()
    assert route.called
    assert route.calls.last.request.headers["authorization"] == f"Bearer {API_KEY}"
    assert resp.datasets[0].name == "gold_ohlcv_1m"
    assert resp.datasets[0].months.latest == "2025-09"


@respx.mock
def test_partitions_passes_filters(api_key: str) -> None:
    route = respx.get(f"{BASE_URL}/v1/datasets/gold_ohlcv_1m").mock(
        return_value=httpx.Response(200, json=PARTITIONS_BODY)
    )
    with TesseraClient() as client:
        resp = client.partitions("gold_ohlcv_1m", coin="BTC", month="2025-09")
    assert resp.partitions[0].size_bytes == 1024
    request = route.calls.last.request
    assert dict(request.url.params) == {"coin": "BTC", "month": "2025-09"}


@respx.mock
def test_download_url_requests_json(api_key: str) -> None:
    route = respx.get(f"{BASE_URL}/v1/datasets/gold_ohlcv_1m/BTC/2025-09/download").mock(
        return_value=httpx.Response(
            200, json={"url": "https://tigris/x.parquet", "expires_at": "2025-09-27T10:45:00Z"}
        )
    )
    with TesseraClient() as client:
        resp = client.download_url("gold_ohlcv_1m", "BTC", "2025-09")
    assert resp.url == "https://tigris/x.parquet"
    assert route.calls.last.request.headers["accept"] == "application/json"


@respx.mock
def test_forbidden_maps_to_exception(api_key: str) -> None:
    respx.get(f"{BASE_URL}/v1/datasets/gold_funding_1h").mock(
        return_value=httpx.Response(403, json={"error": "forbidden"})
    )
    with TesseraClient() as client, pytest.raises(ForbiddenError) as excinfo:
        client.partitions("gold_funding_1h")
    assert excinfo.value.status_code == 403
    assert excinfo.value.code == "forbidden"


@respx.mock
def test_not_found_maps_to_exception(api_key: str) -> None:
    respx.get(f"{BASE_URL}/v1/datasets/nope").mock(
        return_value=httpx.Response(404, json={"error": "not_found"})
    )
    with TesseraClient() as client, pytest.raises(NotFoundError):
        client.partitions("nope")


def test_missing_api_key_raises_configuration_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TESSERA_API_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="No API key"):
        TesseraClient()


def test_explicit_api_key_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TESSERA_API_KEY", raising=False)
    with TesseraClient(api_key="explicit") as client:
        assert client.config.api_key == "explicit"


def test_base_url_trailing_slash_normalized(api_key: str) -> None:
    with TesseraClient(base_url="https://example.com/") as client:
        assert client.config.base_url == "https://example.com"
