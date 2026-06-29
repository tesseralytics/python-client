# AUTO-GENERATED from openapi.json by datamodel-code-generator — DO NOT EDIT. Run: make codegen

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


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
        str, Field(description='Coin symbol, e.g. `BTC`.', examples=['BTC'])
    ]
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
    size_bytes: Annotated[int, Field(description='Parquet object size in bytes.')]


class PartitionsResponse(BaseModel):
    asset: Annotated[str, Field(description='Dataset name the partitions belong to.')]
    generated_at: Annotated[
        str, Field(description='RFC3339 timestamp the catalog manifest was generated.')
    ]
    partitions: list[Partition]


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
