"""Load Tessera partitions into Polars frames.

Reads happen directly over the presigned HTTPS URL via range requests — only
the Parquet footer and the row-groups/columns a query touches cross the wire.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from ..errors import PresignExpiredError
from ._common import ResolvedPartition, require

if TYPE_CHECKING:
    import polars as pl

# Substrings that signal a presigned URL was rejected (typically expired).
_EXPIRY_MARKERS = ("403", "expired", "accessdenied", "access denied", "forbidden")


def _polars() -> Any:
    return require("polars", "polars")


def ensure_available() -> None:
    """Raise :class:`MissingDependencyError` early if Polars is not installed."""
    _polars()


def build_lazyframe(
    parts: Sequence[ResolvedPartition],
    *,
    columns: Sequence[str] | None = None,
) -> pl.LazyFrame:
    """Build a (possibly concatenated) ``LazyFrame`` over the resolved partitions.

    For multi-partition reads, a ``coin`` and ``month`` column identifying the
    source partition are appended so rows stay attributable after concatenation.
    """
    pl = _polars()
    multi = len(parts) > 1
    frames: list[pl.LazyFrame] = []
    for ref, url in parts:
        lf = pl.scan_parquet(url)
        if columns is not None:
            lf = lf.select(columns)
        if multi:
            lf = lf.with_columns(
                pl.lit(ref.coin).alias("coin"),
                pl.lit(ref.month).alias("month"),
            )
        frames.append(lf)
    if len(frames) == 1:
        return frames[0]
    return pl.concat(frames, how="vertical_relaxed")


def collect(lazyframe: pl.LazyFrame) -> pl.DataFrame:
    """Collect a lazy frame, translating presign-expiry failures into a clear error."""
    try:
        return lazyframe.collect()
    except Exception as exc:
        message = str(exc).lower()
        if any(marker in message for marker in _EXPIRY_MARKERS):
            raise PresignExpiredError(
                "A presigned download URL was rejected (likely expired). "
                "Presigned URLs are short-lived — call scan()/read() again to mint fresh ones."
            ) from exc
        raise
