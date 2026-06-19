"""Fetch several partitions concurrently with the async client.

Presigned URLs for every (coin, month) are minted in parallel, then read.

Run:
    pip install "tessera-client[polars]"
    python examples/05_async_concurrent.py
"""

from __future__ import annotations

import asyncio

import polars as pl

import tessera


async def main() -> None:
    async with tessera.AsyncTesseraClient() as client:
        df = await client.read(
            "gold_ohlcv_1m",
            coin=["BTC", "ETH", "SOL", "HYPE"],
            month="2026-05",
            columns=["time", "close", "volume"],
        )
    by_coin = df.group_by("coin").agg(pl.col("volume").sum().alias("total_volume"))
    print(by_coin.sort("total_volume", descending=True))


if __name__ == "__main__":
    asyncio.run(main())
