"""Helpers shared by the Polars and DuckDB readers."""

from __future__ import annotations

from importlib import import_module
from itertools import product
from types import ModuleType

from ..errors import MissingDependencyError
from ..models import Coins, Months, PartitionRef, normalize_coins, normalize_months

# A resolved partition: its reference plus a freshly-minted presigned URL.
ResolvedPartition = tuple[PartitionRef, str]


def require(module: str, extra: str) -> ModuleType:
    """Import an optional dependency or raise a helpful error."""
    try:
        return import_module(module)
    except ImportError as exc:  # pragma: no cover - exercised via monkeypatch
        raise MissingDependencyError(
            f"{module!r} is required for this feature. "
            f'Install it with: pip install "tessera-api[{extra}]"'
        ) from exc


def frame_to_pandas(frame: object) -> object:
    """Convert a Polars frame to pandas, requiring the ``pandas`` extra."""
    require("pandas", "pandas")
    return frame.to_pandas()  # type: ignore[attr-defined]


def expand_refs(asset: str, coin: Coins, month: Months) -> list[PartitionRef]:
    """Expand ``(asset, coins, months)`` into the cartesian list of partitions."""
    coins = normalize_coins(coin)
    months = normalize_months(month)
    if not coins:
        raise ValueError("at least one coin is required")
    if not months:
        raise ValueError("at least one month is required")
    return [PartitionRef(asset, c, m) for c, m in product(coins, months)]
