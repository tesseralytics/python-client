"""Public data models.

Response models (:class:`DatasetsResponse`, :class:`PartitionsResponse`, …) are
generated from the live OpenAPI spec — see ``make codegen``. This module
re-exports them alongside a couple of hand-written ergonomic helpers
(:class:`PartitionRef`, :class:`MonthSpan`).
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from ._generated.models import (
    DatasetsResponse,
    DatasetSummary,
    DownloadResponse,
    ErrorBody,
    MonthRange,
    Partition,
    PartitionsResponse,
)

__all__ = [
    "Coins",
    "DatasetSummary",
    "DatasetsResponse",
    "DownloadResponse",
    "ErrorBody",
    "MonthRange",
    "MonthSpan",
    "Months",
    "Partition",
    "PartitionRef",
    "PartitionsResponse",
]

_MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _validate_month(month: str) -> str:
    if not _MONTH_RE.match(month):
        raise ValueError(f"month must be in YYYY-MM format, got {month!r}")
    return month


@dataclass(frozen=True, slots=True)
class PartitionRef:
    """A fully-qualified reference to a single partition.

    A partition is one ``(asset, coin, month)`` Parquet object, e.g.
    ``gold_ohlcv_1m`` / ``BTC`` / ``2025-09``.
    """

    asset: str
    coin: str
    month: str

    def __post_init__(self) -> None:
        _validate_month(self.month)

    @property
    def object_key(self) -> str:
        """The object-storage key layout: ``{asset}/coin={COIN}/month={YYYY-MM}.parquet``."""
        return f"{self.asset}/coin={self.coin}/month={self.month}.parquet"


@dataclass(frozen=True, slots=True)
class MonthSpan:
    """An inclusive range of months, e.g. ``MonthSpan("2025-01", "2025-09")``.

    Pass it anywhere a ``month`` argument is accepted to expand to every month
    in the range (inclusive of both endpoints).
    """

    start: str
    end: str

    def __post_init__(self) -> None:
        _validate_month(self.start)
        _validate_month(self.end)
        if self.start > self.end:
            raise ValueError(f"MonthSpan start {self.start!r} is after end {self.end!r}")

    def __iter__(self) -> Iterator[str]:
        year, month = (int(p) for p in self.start.split("-"))
        end_year, end_month = (int(p) for p in self.end.split("-"))
        while (year, month) <= (end_year, end_month):
            yield f"{year:04d}-{month:02d}"
            month += 1
            if month > 12:
                month = 1
                year += 1

    def months(self) -> list[str]:
        """Return the months in the span as a list of ``YYYY-MM`` strings."""
        return list(self)


# Accepted shapes for the ``coin`` / ``month`` arguments on reader methods.
Coins = str | Sequence[str]
Months = str | Sequence[str] | MonthSpan


def normalize_coins(coin: Coins) -> list[str]:
    """Coerce a coin argument into a list of coin symbols."""
    return [coin] if isinstance(coin, str) else list(coin)


def normalize_months(month: Months) -> list[str]:
    """Coerce a month argument into a validated list of ``YYYY-MM`` strings."""
    if isinstance(month, MonthSpan):
        return month.months()
    months = [month] if isinstance(month, str) else list(month)
    return [_validate_month(m) for m in months]
