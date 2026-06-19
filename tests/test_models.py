"""Tests for the hand-written model helpers."""

from __future__ import annotations

import pytest

from tessera import MonthSpan, PartitionRef
from tessera.models import normalize_coins, normalize_months


def test_month_span_expands_inclusive_across_year_boundary() -> None:
    assert list(MonthSpan("2024-11", "2025-02")) == [
        "2024-11",
        "2024-12",
        "2025-01",
        "2025-02",
    ]


def test_month_span_single_month() -> None:
    assert MonthSpan("2025-09", "2025-09").months() == ["2025-09"]


def test_month_span_rejects_reversed_range() -> None:
    with pytest.raises(ValueError, match="after end"):
        MonthSpan("2025-09", "2025-01")


@pytest.mark.parametrize("bad", ["2025-13", "2025-00", "25-09", "2025/09", "2025-9"])
def test_invalid_month_format_rejected(bad: str) -> None:
    with pytest.raises(ValueError, match="YYYY-MM"):
        MonthSpan(bad, bad)


def test_partition_ref_object_key() -> None:
    ref = PartitionRef("gold_ohlcv_1m", "BTC", "2025-09")
    assert ref.object_key == "gold_ohlcv_1m/coin=BTC/month=2025-09.parquet"


def test_partition_ref_validates_month() -> None:
    with pytest.raises(ValueError, match="YYYY-MM"):
        PartitionRef("gold_ohlcv_1m", "BTC", "Sept")


def test_normalize_coins_accepts_str_or_sequence() -> None:
    assert normalize_coins("BTC") == ["BTC"]
    assert normalize_coins(["BTC", "ETH"]) == ["BTC", "ETH"]


def test_normalize_months_accepts_span_str_and_list() -> None:
    assert normalize_months("2025-09") == ["2025-09"]
    assert normalize_months(["2025-08", "2025-09"]) == ["2025-08", "2025-09"]
    assert normalize_months(MonthSpan("2025-08", "2025-09")) == ["2025-08", "2025-09"]
