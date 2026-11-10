# Tessera Python Client

**Clean Hyperliquid market data — straight into Polars & DuckDB.**

`tessera-api` is the official Python client for [Tessera](https://tesseralytics.dev):
order-flow-enriched OHLCV, funding-rate, and positioning datasets built from raw Hyperliquid
trade data and delivered as Parquet over a REST API.

Point it at a `(dataset, coin, month)` and get a Polars `LazyFrame` or a DuckDB relation back —
read directly from object storage over range requests, with predicate and projection pushdown.
No temp files, no `pandas` round-trips, no glue code.

```python
import tessera

client = tessera.TesseraClient()  # reads $TESSERA_API_KEY
df = client.read("gold_ohlcv_1m", "BTC", "2026-10")
print(df.select("time", "close", "cvd").tail())
```

## Install

```bash
pip install "tessera-api[polars]"     # headline path
pip install "tessera-api[duckdb]"      # query with SQL
pip install "tessera-api[all]"         # polars + duckdb + pandas
```

Get a free API key (no card required) at [tesseralytics.dev](https://tesseralytics.dev).

## Pricing & history

The free key is the product, not a sample: **$0, no card**, all three datasets over every market
we carry — HIP-3 and `xyz:` perps included — for the trailing 30 days (the current and previous
month objects). There is no subscription.

History is the only paid axis. One-off bundles sell the closed months finalised at purchase,
frozen and perpetual, with every key on your account inheriting the grant:

| Bundle | Price (once) | Markets |
| --- | --- | --- |
| Tessera Majors | $19 | BTC, ETH, SOL, HYPE |
| Tessera HIP-3 (xyz) | $24 | Every `xyz:` deployer market |
| Tessera All Markets | $29 | Every coin Tessera publishes |

A month older than your window returns `404`. See [pricing](https://tesseralytics.dev/pricing).

## Why it's fast

- **Remote range reads** — only the Parquet footer and the row-groups/columns your query touches
  are fetched.
- **Lazy by default** — build a query graph across many months, then `.collect()` once.
- **Parquet end-to-end** — never detours through CSV or `pandas`.

## Next steps

- [Quickstart](quickstart.md)
- [Recipes](recipes/ohlcv-polars.md)
- [Dataset reference](datasets.md)
- [API reference](api.md)
