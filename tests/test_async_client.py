"""Async client parity tests."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from tessera import AsyncTesseraClient, ForbiddenError
from tests.conftest import API_KEY, BASE_URL
from tests.test_client import DATASETS_BODY


@respx.mock
async def test_async_datasets(api_key: str) -> None:
    route = respx.get(f"{BASE_URL}/v1/datasets").mock(
        return_value=httpx.Response(200, json=DATASETS_BODY)
    )
    async with AsyncTesseraClient() as client:
        resp = await client.datasets()
    assert resp.datasets[0].name == "gold_ohlcv_1m"
    assert route.calls.last.request.headers["authorization"] == f"Bearer {API_KEY}"


@respx.mock
async def test_async_forbidden(api_key: str) -> None:
    respx.get(f"{BASE_URL}/v1/datasets/gold_funding_1h").mock(
        return_value=httpx.Response(403, json={"error": "forbidden"})
    )
    async with AsyncTesseraClient() as client:
        with pytest.raises(ForbiddenError):
            await client.partitions("gold_funding_1h")


@respx.mock
async def test_async_read_multi_partition(parquet_factory: Any, api_key: str) -> None:
    for coin in ("BTC", "ETH"):
        url = parquet_factory(coin, "2025-09")
        respx.get(f"{BASE_URL}/v1/datasets/gold_ohlcv_1m/{coin}/2025-09/download").mock(
            return_value=httpx.Response(200, json={"url": url, "expires_at": "t"})
        )
    async with AsyncTesseraClient() as client:
        df = await client.read("gold_ohlcv_1m", ["BTC", "ETH"], "2025-09")
    assert df.height == 10
    assert set(df["coin"].unique()) == {"BTC", "ETH"}
