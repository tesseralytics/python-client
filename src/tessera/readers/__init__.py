"""Optional data-loading backends (Polars, DuckDB).

These modules import their engine lazily, so the core ``tessera`` install stays
dependency-light. Install the extra you want, e.g. ``tessera-client[polars]``.
"""
