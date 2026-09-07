# AUTO-GENERATED from openapi.json by datamodel-code-generator — DO NOT EDIT. Run: make codegen

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class CatalogEntry(BaseModel):
    """
    A dataset's catalog card (the high-level list view). Drill into
    `/v1/catalog/{name}` for the full column dictionary.
    """

    cadence: Annotated[str, Field(description='Granularity + partitioning.')]
    category: Annotated[
        str,
        Field(
            description='Presentation category, e.g. `raw-tiles` / `forecast-layer`.'
        ),
    ]
    column_count: Annotated[
        int, Field(description='Number of documented columns.', ge=0)
    ]
    name: Annotated[
        str,
        Field(
            description='Dataset name / asset key, e.g. `gold_ohlcv_1m`.',
            examples=['gold_ohlcv_1m'],
        ),
    ]
    summary: Annotated[str, Field(description='One-line intuitive summary.')]
    tier: Annotated[
        str,
        Field(
            description='Display tier badge (`free` / `pro`), derived from the access policy.'
        ),
    ]
    title: Annotated[str, Field(description='Human-friendly title.')]


class CatalogResponse(BaseModel):
    datasets: list[CatalogEntry]
    generated_at: Annotated[
        str, Field(description='RFC3339 timestamp the dictionary was generated.')
    ]


class ColumnDoc(BaseModel):
    """
    One column's dictionary entry: the engineering facts (type/nullability/how
    it's computed) plus the plain-English `meaning` (what it is and why you'd care).
    """

    description: Annotated[
        str | None,
        Field(
            description='Technical description — *how* the column is computed. May be absent.'
        ),
    ] = None
    meaning: Annotated[
        str,
        Field(
            description="Plain-English meaning — *what* the column is and why it's useful."
        ),
    ]
    name: Annotated[str, Field(description='Column name.')]
    nullable: Annotated[bool, Field(description='Whether the column may be null.')]
    type: Annotated[
        str, Field(description='Arrow type string, e.g. `float64`, `timestamp[us]`.')
    ]


class ColumnGroup(BaseModel):
    """
    A labelled section of columns within a dataset.
    """

    columns: list[ColumnDoc]
    label: Annotated[
        str | None,
        Field(description='Section heading, or `null` for a single unlabelled group.'),
    ] = None
    meaning: Annotated[
        str | None,
        Field(
            description='Group-level plain-English meaning, used for large column families (e.g.\nthe residualized factor backbone) where a per-column line adds no value.'
        ),
    ] = None
    window: Annotated[
        str | None,
        Field(
            description="Temporal window of this group's fields relative to the timestamp label:\none of `point_in_time`, `backward`, `forward`, `contemporaneous`,\n`static`. Null when the dataset-level `temporal.convention` covers them."
        ),
    ] = None


class DownloadResponse(BaseModel):
    expires_at: Annotated[
        str, Field(description='RFC3339 timestamp at which the URL expires.')
    ]
    url: Annotated[
        str, Field(description='Presigned Tigris URL for the parquet object.')
    ]


class ErrorBody(BaseModel):
    """
    The error response body. Every error variant serialises to this shape —
    a single machine-readable `error` code. Declared as a real struct (rather
    than the inline `json!` below) only so it can be referenced as a response
    `body` in the OpenAPI spec; `into_response` still emits the same JSON.
    """

    error: Annotated[
        str,
        Field(
            description='Machine-readable error code, e.g. `not_found`, `unauthorized`.',
            examples=['not_found'],
        ),
    ]


class MonthRange(BaseModel):
    earliest: Annotated[
        str | None, Field(description='Earliest partition month (`YYYY-MM`), if any.')
    ] = None
    latest: Annotated[
        str | None, Field(description='Latest partition month (`YYYY-MM`), if any.')
    ] = None


class Partition(BaseModel):
    coin: Annotated[
        str | None,
        Field(
            description='Coin symbol, e.g. `BTC`. Absent (`None`) for market-wide (coinless)\ndatasets whose parquet is one row per month with no coin dimension —\nnone are currently published.',
            examples=['BTC'],
        ),
    ] = None
    coverage: Annotated[
        float | None,
        Field(
            description='Fraction of the expected time-buckets that are populated (`rows` ÷\nelapsed buckets) — the tradable-universe signal: the 1-minute grid is\ntrade-driven and gappy on thin coins, the hourly grids near-complete.\nPresent alongside `rows`; `None` elsewhere.'
        ),
    ] = None
    is_open: Annotated[
        bool | None,
        Field(
            description='Whether this is the current, in-progress month — its parquet is\nre-materialised daily (part-month freshness) and therefore grows under\nthe customer. Absent (`None`) in older (v1) manifests.'
        ),
    ] = None
    modified_at: Annotated[
        str | None, Field(description='RFC3339 timestamp of the last write, if known.')
    ] = None
    month: Annotated[
        str, Field(description='Partition month, `YYYY-MM`.', examples=['2025-09'])
    ]
    rows: Annotated[
        int | None,
        Field(
            description='Row count (parquet `num_rows`). Present only for the time-series tiles\n(`gold_ohlcv_1m`, `gold_funding_1h`, `gold_positioning_1h`) from v3\nmanifests; `None` elsewhere and in older manifests.'
        ),
    ] = None
    size_bytes: Annotated[int, Field(description='Parquet object size in bytes.')]


class PartitionsResponse(BaseModel):
    asset: Annotated[str, Field(description='Dataset name the partitions belong to.')]
    generated_at: Annotated[
        str, Field(description='RFC3339 timestamp the catalog manifest was generated.')
    ]
    partitions: list[Partition]


class Temporal(BaseModel):
    """
    The dataset's temporal contract — what the timestamp column marks and the
    look-ahead-safety rules for joining. Mirror of the resolver's `temporal`
    block (`semantic/__init__.py`).
    """

    convention: Annotated[
        str,
        Field(description='One-paragraph plain-English join / look-ahead contract.'),
    ]
    grain: Annotated[
        str, Field(description='Observation width, e.g. `1m`, `1h`, `1d`, `1mo`.')
    ]
    label: Annotated[
        str,
        Field(
            description='What the label marks: one of `interval_start`, `interval_end`,\n`snapshot`, `forecast_target`.'
        ),
    ]
    timestamp_field: Annotated[
        str,
        Field(
            description='Which column carries the label, e.g. `time`, `day`, `month_start`.'
        ),
    ]


class DatasetDoc(BaseModel):
    """
    One dataset's catalog entry + full data dictionary.
    """

    cadence: Annotated[
        str,
        Field(
            description='Granularity + partitioning, e.g. "1-minute bars, partitioned per (coin, month)".'
        ),
    ]
    category: Annotated[
        str,
        Field(
            description='Presentation category, e.g. `raw-tiles` or `forecast-layer`.'
        ),
    ]
    column_count: Annotated[
        int, Field(description='Number of documented columns.', ge=0)
    ]
    column_groups: Annotated[
        list[ColumnGroup],
        Field(description='Columns, grouped for presentation, in schema order.'),
    ]
    description: Annotated[
        str, Field(description='Longer prose — the dictionary page header.')
    ]
    direct_answer: Annotated[
        str | None,
        Field(
            description='40-60 word keyword-first lead answer — the definitional "what is this"\nblurb, and the strongest AI-citation extraction target. Defaulted for\nforward/backward compatibility with snapshots predating the field.'
        ),
    ] = None
    keywords: Annotated[
        list[str] | None,
        Field(
            description='Per-dataset discovery keywords (schema.org keywords on the web).'
        ),
    ] = None
    name: Annotated[
        str,
        Field(
            description='Dataset name / asset key, e.g. `gold_ohlcv_1m`.',
            examples=['gold_ohlcv_1m'],
        ),
    ]
    note: Annotated[
        str | None, Field(description='Optional "how to use this" callout.')
    ] = None
    seo_title: Annotated[
        str | None,
        Field(
            description='Keyword-first SEO title tag (web `<title>`). Defaulted so older snapshots\nwithout the field still deserialize.'
        ),
    ] = None
    summary: Annotated[
        str, Field(description='One-line intuitive summary — the catalog card.')
    ]
    temporal: Annotated[
        Temporal | None,
        Field(
            description='Machine-readable timestamp/interval contract: what the label marks and\nhow to join without leaking the future. Defaulted so snapshots predating\nthe field still deserialize.'
        ),
    ] = None
    tier: Annotated[
        str,
        Field(
            description='Display tier: `free` or `pro`. Re-derived from `policy.rs` on read, so it\nalways matches actual entitlement regardless of the on-disk value.'
        ),
    ]
    title: Annotated[
        str,
        Field(description='Human-friendly title, e.g. "Order-flow OHLCV (1-minute)".'),
    ]
    use_case: Annotated[
        str | None,
        Field(description='One-line "what you\'d use it for" (buyer-intent) copy.'),
    ] = None


class DatasetSummary(BaseModel):
    coins: Annotated[list[str], Field(description='Distinct coins present, sorted.')]
    months: MonthRange
    name: Annotated[
        str,
        Field(
            description='Dataset name, e.g. `gold_ohlcv_1m`.',
            examples=['gold_ohlcv_1m'],
        ),
    ]
    partition_count: Annotated[
        int, Field(description='Number of partitions visible to the caller.', ge=0)
    ]


class DatasetsResponse(BaseModel):
    datasets: list[DatasetSummary]
    generated_at: Annotated[
        str, Field(description='RFC3339 timestamp the catalog manifest was generated.')
    ]
