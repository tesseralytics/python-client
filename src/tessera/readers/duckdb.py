"""Load Tessera partitions into DuckDB relations.

Uses DuckDB's ``httpfs`` to range-read the presigned Parquet directly; the
returned relation can be filtered/aggregated in SQL with predicate pushdown.
"""

from __future__ import annotations

import contextlib
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from ._common import ResolvedPartition, require

if TYPE_CHECKING:
    import duckdb


def _duckdb() -> Any:
    return require("duckdb", "duckdb")


def ensure_available() -> None:
    """Raise :class:`MissingDependencyError` early if DuckDB is not installed."""
    _duckdb()


def _sql_str(value: str) -> str:
    """Quote a value as a SQL string literal."""
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def _ensure_httpfs(con: duckdb.DuckDBPyConnection) -> None:
    # Recent DuckDB autoloads httpfs for https paths; load explicitly but don't
    # fail if the environment can't reach the extension repository.
    with contextlib.suppress(Exception):
        con.execute("INSTALL httpfs; LOAD httpfs;")


def build_relation(
    parts: Sequence[ResolvedPartition],
    *,
    connection: duckdb.DuckDBPyConnection | None = None,
    columns: Sequence[str] | None = None,
) -> duckdb.DuckDBPyRelation:
    """Build a DuckDB relation over the resolved partitions.

    For multi-partition reads each leaf is unioned with a ``coin`` and ``month``
    column identifying the source partition.
    """
    duckdb = _duckdb()
    con = connection if connection is not None else duckdb.connect()
    _ensure_httpfs(con)

    multi = len(parts) > 1
    select_cols = ", ".join(columns) if columns else "*"
    selects: list[str] = []
    for ref, url in parts:
        projection = select_cols
        if multi:
            projection = (
                f"{select_cols}, {_sql_str(ref.coin)} AS coin, {_sql_str(ref.month)} AS month"
            )
        selects.append(f"SELECT {projection} FROM read_parquet({_sql_str(url)})")
    query = "\nUNION ALL\n".join(selects)
    return con.sql(query)
