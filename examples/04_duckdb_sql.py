"""Query Tessera partitions with DuckDB SQL.

Run:
    pip install "tessera-api[duckdb]"
    python examples/04_duckdb_sql.py
"""

from __future__ import annotations

import tessera


def main() -> None:
    with tessera.TesseraClient() as client:
        rel = client.to_duckdb("gold_ohlcv_1m", ["BTC", "ETH"], "2026-05")

        # `rel` is a DuckDB relation — keep composing in SQL.
        summary = rel.aggregate(
            "coin, count(*) AS minutes, round(avg(cvd), 2) AS mean_cvd, max(high) AS high",
            "coin",
        )
        summary.show()


if __name__ == "__main__":
    main()
