# Query Hyperliquid funding rates with DuckDB SQL

The `gold_funding_1h` dataset gives you hourly funding rates. Open it as a DuckDB relation
and stay in SQL — DuckDB range-reads the Parquet and pushes predicates down to row groups.

```python
import tessera

with tessera.TesseraClient() as client:
    rel = client.to_duckdb(
        "gold_funding_1h",
        coin=["BTC", "ETH"],
        month=tessera.MonthSpan("2026-09", "2026-10"),
    )

    # Average funding by coin and the most extreme hours.
    rel.aggregate("coin, avg(funding_rate) AS mean_funding", "coin").show()
```

## Bring your own connection

Pass an existing connection to join Tessera data against your own tables:

```python
import duckdb

con = duckdb.connect("research.db")
rel = client.to_duckdb("gold_funding_1h", "BTC", "2026-10", connection=con)
rel.create_view("btc_funding")
con.sql("SELECT * FROM btc_funding JOIN my_positions USING (time)").show()
```

!!! tip
    Every dataset is on the free key, but only for the trailing 30 days. A month outside your
    window returns `tessera.NotFoundError` — buy the one-off bundle that covers it. See
    [pricing](https://tesseralytics.dev/pricing).
