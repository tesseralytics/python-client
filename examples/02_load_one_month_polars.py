"""Load one month of BTC minute candles straight into a Polars DataFrame.

The Parquet is read remotely over range requests — no temp files.

Run:
    pip install "tessera-client[polars]"
    python examples/02_load_one_month_polars.py
"""

from __future__ import annotations

import polars as pl

import tessera


def main() -> None:
    with tessera.TesseraClient() as client:
        df = client.read("gold_ohlcv_1m", "BTC", "2026-05")

    print(f"{df.height:,} rows x {df.width} columns")
    print(df.columns)

    # Hourly close + cumulative volume delta from the minute candles.
    # `time` arrives as a proper Datetime, so resampling needs no parsing.
    hourly = (
        df.sort("time")
        .group_by_dynamic("time", every="1h")
        .agg(pl.col("close").last(), pl.col("cvd").sum().alias("hourly_cvd"))
        .sort("time")
    )
    print(hourly.tail())


if __name__ == "__main__":
    main()
