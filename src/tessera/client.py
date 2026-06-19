"""Synchronous Tessera API client."""

from __future__ import annotations

import time
from collections.abc import Sequence
from types import TracebackType
from typing import TYPE_CHECKING

import httpx

from . import _base, _resolver
from .config import DEFAULT_BASE_URL, ClientConfig, backoff_delay, resolve_api_key
from .errors import NetworkError
from .models import (
    Coins,
    DatasetsResponse,
    DownloadResponse,
    Months,
    PartitionRef,
    PartitionsResponse,
)
from .readers import duckdb as _duckdb_reader
from .readers import polars as _polars_reader
from .readers._common import expand_refs, frame_to_pandas

if TYPE_CHECKING:
    import duckdb
    import pandas
    import polars as pl

__all__ = ["TesseraClient"]


class TesseraClient:
    """A synchronous client for the Tessera API.

    Args:
        api_key: Your Tessera API key. Falls back to ``$TESSERA_API_KEY``.
        base_url: API base URL. Defaults to the production endpoint.
        timeout: Per-request timeout in seconds.
        max_retries: Retries for transient failures (429/5xx, network errors).
        http_client: Inject your own ``httpx.Client`` (advanced; overrides the
            timeout/base-url defaults — you are responsible for auth headers).

    Example:
        >>> client = TesseraClient()
        >>> df = client.read("gold_ohlcv_1m", "BTC", "2025-09")
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        max_retries: int = 3,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.config = ClientConfig(
            api_key=resolve_api_key(api_key),
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        if http_client is not None:
            self._http = http_client
            self._owns_http = False
        else:
            self._http = httpx.Client(**_base.build_httpx_kwargs(self.config))  # type: ignore[arg-type]
            self._owns_http = True

    # -- lifecycle ---------------------------------------------------------
    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> TesseraClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    # -- transport ---------------------------------------------------------
    def _request(self, prepared: _base.PreparedRequest) -> httpx.Response:
        for attempt in range(self.config.max_retries + 1):
            last = attempt == self.config.max_retries
            try:
                response = self._http.get(prepared.path, params=prepared.params or None)
            except httpx.TransportError as exc:
                if last:
                    raise NetworkError(f"network error contacting Tessera: {exc}") from exc
                time.sleep(backoff_delay(attempt, None))
                continue
            if not last and _base.should_retry(response.status_code):
                time.sleep(backoff_delay(attempt, _base.parse_retry_after(response)))
                continue
            _base.raise_for_status(response)
            return response
        raise AssertionError("unreachable")  # pragma: no cover

    # -- metadata endpoints ------------------------------------------------
    def datasets(self) -> DatasetsResponse:
        """List every dataset visible to your plan."""
        response = self._request(_base.datasets_request())
        return DatasetsResponse.model_validate_json(response.content)

    def partitions(
        self,
        asset: str,
        *,
        coin: str | None = None,
        month: str | None = None,
    ) -> PartitionsResponse:
        """List the partitions of ``asset``, optionally filtered by coin/month."""
        response = self._request(_base.partitions_request(asset, coin, month))
        return PartitionsResponse.model_validate_json(response.content)

    def download_url(self, asset: str, coin: str, month: str) -> DownloadResponse:
        """Mint a short-lived presigned download URL for one partition."""
        response = self._request(_base.download_request(asset, coin, month))
        return DownloadResponse.model_validate_json(response.content)

    # -- partition helpers -------------------------------------------------
    def partition_refs(self, asset: str, coin: Coins, month: Months) -> list[PartitionRef]:
        """Expand ``(asset, coins, months)`` into concrete partition references."""
        return expand_refs(asset, coin, month)

    def _resolve(self, refs: Sequence[PartitionRef]) -> list[_resolver.ResolvedPartition]:
        return _resolver.resolve_sync(
            lambda ref: self.download_url(ref.asset, ref.coin, ref.month).url,
            refs,
        )

    # -- data loading ------------------------------------------------------
    def scan(
        self,
        asset: str,
        coin: Coins,
        month: Months,
        *,
        columns: Sequence[str] | None = None,
    ) -> pl.LazyFrame:
        """Lazily scan one or more partitions into a Polars ``LazyFrame``.

        URLs are minted now but the data is read on ``.collect()``. Because
        presigned URLs expire (~15 min), collect promptly; for long-lived graphs
        re-run ``scan`` to refresh.
        """
        _polars_reader.ensure_available()
        parts = self._resolve(expand_refs(asset, coin, month))
        return _polars_reader.build_lazyframe(parts, columns=columns)

    def read(
        self,
        asset: str,
        coin: Coins,
        month: Months,
        *,
        columns: Sequence[str] | None = None,
    ) -> pl.DataFrame:
        """Eagerly read one or more partitions into a Polars ``DataFrame``."""
        _polars_reader.ensure_available()
        parts = self._resolve(expand_refs(asset, coin, month))
        return _polars_reader.collect(_polars_reader.build_lazyframe(parts, columns=columns))

    def to_duckdb(
        self,
        asset: str,
        coin: Coins,
        month: Months,
        *,
        connection: duckdb.DuckDBPyConnection | None = None,
        columns: Sequence[str] | None = None,
    ) -> duckdb.DuckDBPyRelation:
        """Open one or more partitions as a DuckDB relation for SQL querying."""
        _duckdb_reader.ensure_available()
        parts = self._resolve(expand_refs(asset, coin, month))
        return _duckdb_reader.build_relation(parts, connection=connection, columns=columns)

    def to_pandas(
        self,
        asset: str,
        coin: Coins,
        month: Months,
        *,
        columns: Sequence[str] | None = None,
    ) -> pandas.DataFrame:
        """Convenience escape hatch: read into a pandas ``DataFrame`` (via Polars)."""
        frame = self.read(asset, coin, month, columns=columns)
        return frame_to_pandas(frame)  # type: ignore[return-value]
