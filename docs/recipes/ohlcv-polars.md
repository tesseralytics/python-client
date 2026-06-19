# Load Hyperliquid OHLCV into Polars

Pull order-flow-enriched minute candles for any coin and resample them in Polars — read straight
from object storage, no temp files.

```python
import polars as pl
import tessera

with tessera.TesseraClient() as client:
    df = client.read("gold_ohlcv_1m", "BTC", "2026-05")

hourly = (
    df.sort("time")
    .group_by_dynamic("time", every="1h")
    .agg(
        pl.col("open").first(),
        pl.col("high").max(),
        pl.col("low").min(),
        pl.col("close").last(),
        pl.col("volume").sum(),
    )
    .sort("time")
)
print(hourly.tail())
```

## Multiple months, lazily

Use `scan` for a `LazyFrame` and let Polars push your projection/filter down into the remote
reads:

```python
lf = client.scan(
    "gold_ohlcv_1m",
    coin="BTC",
    month=tessera.MonthSpan("2025-10", "2026-05"),
    columns=["time", "close"],
)
returns = (
    lf.sort("time")
    .with_columns(pl.col("close").pct_change().alias("ret"))
    .collect()
)
```

Reading several coins at once adds a `coin` column so you can `group_by("coin")`.
