# Backtesting with CVD & aggressor delta

Tessera's `gold_ohlcv_1m` candles ship with order-flow microstructure baked in — cumulative
volume delta (`cvd`) and per-bar `aggressor_delta` — so you can prototype flow-driven signals
without reconstructing the tape.

```python
import polars as pl
import tessera

with tessera.TesseraClient() as client:
    lf = client.scan(
        "gold_ohlcv_1m",
        coin="BTC",
        month=tessera.MonthSpan("2026-01", "2026-05"),
        columns=["time", "close", "cvd", "aggressor_delta"],
    )

signal = (
    lf.sort("time")
    # Go long when aggressive buying dominates over a 15-bar window.
    .with_columns(pl.col("aggressor_delta").rolling_sum(15).alias("flow"))
    .with_columns((pl.col("flow") > 0).cast(pl.Int8).alias("position"))
    .with_columns(pl.col("close").pct_change().alias("ret"))
    .with_columns((pl.col("position").shift(1) * pl.col("ret")).alias("strategy_ret"))
    .collect()
)

equity = signal.select(pl.col("strategy_ret").fill_null(0).cum_sum().alias("equity"))
print(equity.tail())
```

Because `scan` is lazy, only the four columns above are read from each month's Parquet — the rest
of the file never leaves object storage.
