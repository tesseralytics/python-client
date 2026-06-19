"""Lazily scan many months and let Polars push the filter down to the reads.

`scan` returns a LazyFrame; nothing is fetched until `.collect()`, and only the
row-groups/columns the query needs cross the wire.

Run:
    pip install "tessera-client[polars]"
    python examples/03_multi_month_lazy.py
"""

from __future__ import annotations

import polars as pl

import tessera


def main() -> None:
    with tessera.TesseraClient() as client:
        lf = client.scan(
            "gold_ohlcv_1m",
            coin=["BTC", "ETH"],
            month=tessera.MonthSpan("2026-01", "2026-05"),
            columns=["time", "close", "aggressor_delta"],
        )

        # Only large-aggressor prints, computed lazily across all partitions.
        result = (
            lf.filter(pl.col("aggressor_delta").abs() > 1_000)
            .group_by("coin")
            .agg(pl.len().alias("big_prints"), pl.col("aggressor_delta").mean().alias("avg_delta"))
            .collect()
        )
    print(result)


if __name__ == "__main__":
    main()
