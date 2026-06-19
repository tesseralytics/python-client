<div align="center">

# tessera-api

**Clean Hyperliquid market data — straight into Polars & DuckDB.**

[![PyPI](https://img.shields.io/pypi/v/tessera-api.svg)](https://pypi.org/project/tessera-api/)
[![Python](https://img.shields.io/pypi/pyversions/tessera-api.svg)](https://pypi.org/project/tessera-api/)
[![CI](https://github.com/tesseralytics/python-client/actions/workflows/ci.yml/badge.svg)](https://github.com/tesseralytics/python-client/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

The official Python client for [**Tessera**](https://tesseralytics.dev) — order-flow-enriched
OHLCV, funding-rate, and positioning datasets built from raw Hyperliquid trade data,
delivered as Parquet over a REST API.

</div>

---

`tessera-api` is built for quants and analysts who would rather write a query than babysit a
download. Point it at a `(dataset, coin, month)` and get a **Polars `LazyFrame`** or a **DuckDB
relation** back — read straight from object storage over range requests, with predicate and
projection pushdown. No temp files, no `pandas` round-trips, no glue code.

## Install

```bash
pip install "tessera-api[polars]"     # the headline path
pip install "tessera-api[duckdb]"      # query with SQL instead
pip install "tessera-api[all]"         # polars + duckdb + pandas escape hatch
```

Grab a free API key (no card required) at **[tesseralytics.dev](https://tesseralytics.dev)** and
export it:

```bash
export TESSERA_API_KEY="sk_..."
```

## Quickstart

```python
import polars as pl
import tessera

client = tessera.TesseraClient()  # reads $TESSERA_API_KEY

# Browse the catalog
for ds in client.datasets().datasets:
    print(ds.name, ds.coins, ds.months.earliest, "→", ds.months.latest)

# One month of BTC minute candles → a Polars DataFrame. Read remotely, no temp files.
df = client.read("gold_ohlcv_1m", "BTC", "2026-05")
print(df.select("time", "close", "cvd", "vwap").tail())

# Lazy + pushdown: only the bytes you actually need cross the wire.
lf = client.scan("gold_ohlcv_1m", "BTC", tessera.MonthSpan("2025-10", "2026-05"))
big_prints = lf.filter(pl.col("aggressor_delta").abs() > 1_000).collect()
```

Prefer SQL?

```python
rel = client.to_duckdb("gold_ohlcv_1m", ["BTC", "ETH"], "2026-05")
rel.filter("close > open").aggregate("coin, avg(cvd) AS mean_cvd, count(*) AS n", "coin").show()
```

Everything is `async`-native too — swap in `tessera.AsyncTesseraClient` and `await` it.

## Why it's fast

- **Remote range reads.** `scan()` hands Polars (or DuckDB) a presigned Parquet URL; only the
  footer and the row-groups/columns your query touches are fetched.
- **Lazy by default.** Build a query graph across many months, then `.collect()` once.
- **Parquet end-to-end.** Tessera ships columnar Parquet; this client never detours through CSV
  or `pandas`.

## Datasets

| Dataset | Granularity | Tier | Highlights |
| --- | --- | --- | --- |
| `gold_ohlcv_1m` | 1 minute | Free + Pro | OHLCV, CVD, aggressor delta, VWAP, fees |
| `gold_funding_1h` | 1 hour | Pro | Funding rates |
| `gold_positioning_1h` | 1 hour | Pro | Open-interest / positioning analytics |

Free tier covers BTC, ETH, SOL, HYPE. Pro unlocks every coin (including HIP-3 markets) and the
funding/positioning datasets. See **[the docs](https://tesseralytics.dev/python-client)** for the
full column reference and recipes.

## Documentation

- 📚 **Guide & API reference:** <https://tesseralytics.dev/python-client>
- 🧑‍💻 **Runnable examples:** [`examples/`](examples/)
- 🌐 **Product & pricing:** <https://tesseralytics.dev>

## License

MIT © Tessera. See [LICENSE](LICENSE).
