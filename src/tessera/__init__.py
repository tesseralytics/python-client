"""Tessera API client — Hyperliquid datasets straight into Polars & DuckDB.

Quickstart:
    >>> import tessera
    >>> client = tessera.TesseraClient()          # reads $TESSERA_API_KEY
    >>> df = client.read("gold_ohlcv_1m", "BTC", "2025-09")

See https://tesseralytics.dev for an API key and dataset reference.
"""

from __future__ import annotations

from ._version import __version__
from .async_client import AsyncTesseraClient
from .client import TesseraClient
from .errors import (
    AuthenticationError,
    BadRequestError,
    ConfigurationError,
    ForbiddenError,
    InternalServerError,
    MissingDependencyError,
    NetworkError,
    NotFoundError,
    PresignExpiredError,
    ServiceUnavailableError,
    TesseraAPIError,
    TesseraError,
)
from .models import (
    DatasetsResponse,
    DatasetSummary,
    DownloadResponse,
    MonthRange,
    MonthSpan,
    Partition,
    PartitionRef,
    PartitionsResponse,
)

__all__ = [
    "AsyncTesseraClient",
    "AuthenticationError",
    "BadRequestError",
    "ConfigurationError",
    "DatasetSummary",
    # models & helpers
    "DatasetsResponse",
    "DownloadResponse",
    "ForbiddenError",
    "InternalServerError",
    "MissingDependencyError",
    "MonthRange",
    "MonthSpan",
    "NetworkError",
    "NotFoundError",
    "Partition",
    "PartitionRef",
    "PartitionsResponse",
    "PresignExpiredError",
    "ServiceUnavailableError",
    "TesseraAPIError",
    # clients
    "TesseraClient",
    # errors
    "TesseraError",
    "__version__",
]
