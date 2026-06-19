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

client = tessera.TesseraClient()              # reads $TESSERA_API_KEY
df = client.read("gold_ohlcv_1m", "BTC", "2026-05")
print(df.select("time", "close", "cvd").tail())
```

## Install

```bash
pip install "tessera-api[polars]"     # headline path
pip install "tessera-api[duckdb]"      # query with SQL
pip install "tessera-api[all]"         # polars + duckdb + pandas
```

Get a free API key (no card required) at [tesseralytics.dev](https://tesseralytics.dev).

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
