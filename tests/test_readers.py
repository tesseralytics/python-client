"""Tests for the Polars and DuckDB readers and the client data-loading methods."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from tessera import PresignExpiredError, TesseraClient
from tessera.errors import MissingDependencyError
from tessera.models import PartitionRef
from tessera.readers import polars as polars_reader
from tessera.readers._common import expand_refs, require
from tests.conftest import BASE_URL


def _download_route(coin: str, month: str, url: str) -> None:
    respx.get(f"{BASE_URL}/v1/datasets/gold_ohlcv_1m/{coin}/{month}/download").mock(
        return_value=httpx.Response(200, json={"url": url, "expires_at": "2025-09-27T10:45:00Z"})
    )


# -- reader unit tests -----------------------------------------------------
def test_build_lazyframe_single_partition_is_pristine(parquet_factory: Any) -> None:
    url = parquet_factory("BTC", "2025-09")
    lf = polars_reader.build_lazyframe([(PartitionRef("gold_ohlcv_1m", "BTC", "2025-09"), url)])
    df = lf.collect()
    assert "coin" not in df.columns  # no partition columns injected for a single partition
    assert df.height == 5


def test_build_lazyframe_multi_partition_injects_columns(parquet_factory: Any) -> None:
    parts = [
        (PartitionRef("gold_ohlcv_1m", "BTC", "2025-09"), parquet_factory("BTC", "2025-09")),
        (PartitionRef("gold_ohlcv_1m", "ETH", "2025-09"), parquet_factory("ETH", "2025-09")),
    ]
    df = polars_reader.build_lazyframe(parts).collect()
    assert df.height == 10
    assert set(df["coin"].unique()) == {"BTC", "ETH"}
    assert df["month"].unique().to_list() == ["2025-09"]


def test_build_lazyframe_projection(parquet_factory: Any) -> None:
    url = parquet_factory("BTC", "2025-09")
    df = polars_reader.build_lazyframe(
        [(PartitionRef("gold_ohlcv_1m", "BTC", "2025-09"), url)], columns=["time", "close"]
    ).collect()
    assert df.columns == ["time", "close"]


def test_collect_translates_expiry() -> None:
    class _Boom:
        def collect(self) -> Any:
            raise RuntimeError("HTTP status 403 AccessDenied: Request has expired")

    with pytest.raises(PresignExpiredError):
        polars_reader.collect(_Boom())  # type: ignore[arg-type]


def test_collect_reraises_other_errors() -> None:
    class _Boom:
        def collect(self) -> Any:
            raise RuntimeError("schema mismatch")

    with pytest.raises(RuntimeError, match="schema mismatch"):
        polars_reader.collect(_Boom())  # type: ignore[arg-type]


def test_require_missing_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fail(_name: str) -> Any:
        raise ImportError("nope")

    monkeypatch.setattr("tessera.readers._common.import_module", _fail)
    with pytest.raises(MissingDependencyError, match=r"tessera-client\[duckdb\]"):
        require("duckdb", "duckdb")


def test_read_fails_fast_without_polars(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fail(name: str) -> Any:
        if name == "polars":
            raise ImportError("no polars")
        raise AssertionError(name)

    monkeypatch.setattr("tessera.readers._common.import_module", _fail)
    # Must raise before any network call (no respx mock registered).
    with TesseraClient(api_key="x") as client, pytest.raises(MissingDependencyError):
        client.read("gold_ohlcv_1m", "BTC", "2025-09")


def test_expand_refs_cartesian() -> None:
    refs = expand_refs("gold_ohlcv_1m", ["BTC", "ETH"], ["2025-08", "2025-09"])
    assert len(refs) == 4
    assert PartitionRef("gold_ohlcv_1m", "ETH", "2025-08") in refs


# -- client integration ----------------------------------------------------
@respx.mock
def test_client_read(parquet_factory: Any, api_key: str) -> None:
    _download_route("BTC", "2025-09", parquet_factory("BTC", "2025-09"))
    with TesseraClient() as client:
        df = client.read("gold_ohlcv_1m", "BTC", "2025-09")
    assert df.height == 5
    assert "close" in df.columns


@respx.mock
def test_client_read_multi_coin(parquet_factory: Any, api_key: str) -> None:
    _download_route("BTC", "2025-09", parquet_factory("BTC", "2025-09"))
    _download_route("ETH", "2025-09", parquet_factory("ETH", "2025-09"))
    with TesseraClient() as client:
        df = client.read("gold_ohlcv_1m", ["BTC", "ETH"], "2025-09")
    assert df.height == 10
    assert set(df["coin"].unique()) == {"BTC", "ETH"}


@respx.mock
def test_client_to_duckdb(parquet_factory: Any, api_key: str) -> None:
    _download_route("BTC", "2025-09", parquet_factory("BTC", "2025-09"))
    with TesseraClient() as client:
        rel = client.to_duckdb("gold_ohlcv_1m", "BTC", "2025-09")
        count = rel.aggregate("count(*) AS n").fetchone()
    assert count is not None and count[0] == 5


@respx.mock
def test_client_to_pandas(parquet_factory: Any, api_key: str) -> None:
    _download_route("BTC", "2025-09", parquet_factory("BTC", "2025-09"))
    with TesseraClient() as client:
        pdf = client.to_pandas("gold_ohlcv_1m", "BTC", "2025-09", columns=["time", "close"])
    assert list(pdf.columns) == ["time", "close"]
    assert len(pdf) == 5
