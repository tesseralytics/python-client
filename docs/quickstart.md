# Quickstart

## 1. Install & authenticate

```bash
pip install "tessera-client[polars]"
export TESSERA_API_KEY="sk_..."   # from https://tesseralytics.dev
```

The client reads `TESSERA_API_KEY` automatically. You can also pass it explicitly:

```python
client = tessera.TesseraClient(api_key="sk_...")
```

## 2. Browse the catalog

```python
import tessera

with tessera.TesseraClient() as client:
    for ds in client.datasets().datasets:
        print(ds.name, ds.coins, ds.months.earliest, "→", ds.months.latest)
```

## 3. Load data

A single partition into a Polars `DataFrame`:

```python
df = client.read("gold_ohlcv_1m", "BTC", "2026-05")
```

Many partitions, lazily, with column projection and a pushed-down filter:

```python
import polars as pl

lf = client.scan(
    "gold_ohlcv_1m",
    coin=["BTC", "ETH"],
    month=tessera.MonthSpan("2026-01", "2026-05"),
    columns=["time", "close", "cvd"],
)
df = lf.filter(pl.col("cvd") > 0).collect()
```

Multi-partition reads add `coin` and `month` columns so every row stays attributable.

## 4. Or query with SQL

```python
rel = client.to_duckdb("gold_ohlcv_1m", "BTC", "2026-05")
rel.filter("close > open").aggregate("count(*) AS green_minutes").show()
```

## Async

Every method has an `async` twin on `AsyncTesseraClient`:

```python
async with tessera.AsyncTesseraClient() as client:
    df = await client.read("gold_ohlcv_1m", ["BTC", "ETH"], "2026-05")
```

## A note on presigned URLs

Downloads use short-lived presigned URLs (~15 minutes). `read()`/`to_duckdb()` mint a fresh URL
and read immediately. For a `scan()` `LazyFrame`, collect promptly — don't stash it for hours and
collect later. If a URL expires mid-read you'll get a `tessera.PresignExpiredError`; just call
`scan`/`read` again.
