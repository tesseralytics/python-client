"""Shared test fixtures."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import polars as pl
import pytest

BASE_URL = "https://tesseralytics.dev"
API_KEY = "test-key-123"


@pytest.fixture
def api_key(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setenv("TESSERA_API_KEY", API_KEY)
    return API_KEY


def _ohlcv_frame(coin: str, rows: int = 5) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [datetime(2025, 9, 1, 0, i, tzinfo=timezone.utc) for i in range(rows)],
            "open": [100.0 + i for i in range(rows)],
            "high": [101.0 + i for i in range(rows)],
            "low": [99.0 + i for i in range(rows)],
            "close": [100.5 + i for i in range(rows)],
            "volume": [10.0 * (i + 1) for i in range(rows)],
            "cvd": [float(i - 2) for i in range(rows)],
            "aggressor_delta": [float(2 * i - 4) for i in range(rows)],
        }
    )


@pytest.fixture
def parquet_factory(tmp_path: Path) -> Iterator[object]:
    """Return a factory that writes a partition parquet and yields its local path (as a URL)."""

    def make(coin: str = "BTC", month: str = "2025-09", rows: int = 5) -> str:
        path = tmp_path / f"{coin}_{month}.parquet"
        _ohlcv_frame(coin, rows).write_parquet(path)
        return str(path)

    yield make
