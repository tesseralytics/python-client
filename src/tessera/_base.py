"""Transport-agnostic plumbing shared by the sync and async clients.

The two clients differ only in how they *await* I/O; everything else — URL
construction, header building, error mapping, retry decisions — lives here so
there is a single source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

import httpx

from .config import RETRYABLE_STATUSES, ClientConfig
from .errors import error_from_response


def _seg(value: str) -> str:
    """URL-encode a single path segment (no slashes survive)."""
    return quote(value, safe="")


@dataclass(frozen=True, slots=True)
class PreparedRequest:
    """A resolved HTTP request: path + query params, ready to send."""

    path: str
    params: dict[str, str]


def datasets_request() -> PreparedRequest:
    return PreparedRequest("/v1/datasets", {})


def partitions_request(asset: str, coin: str | None, month: str | None) -> PreparedRequest:
    params: dict[str, str] = {}
    if coin is not None:
        params["coin"] = coin
    if month is not None:
        params["month"] = month
    return PreparedRequest(f"/v1/datasets/{_seg(asset)}", params)


def download_request(asset: str, coin: str, month: str) -> PreparedRequest:
    path = f"/v1/datasets/{_seg(asset)}/{_seg(coin)}/{_seg(month)}/download"
    return PreparedRequest(path, {})


def parse_retry_after(response: httpx.Response) -> float | None:
    """Parse the ``Retry-After`` header (seconds form only) if present."""
    raw = response.headers.get("retry-after")
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def should_retry(status_code: int) -> bool:
    return status_code in RETRYABLE_STATUSES


def raise_for_status(response: httpx.Response) -> None:
    """Raise the mapped :class:`TesseraAPIError` for a non-2xx response."""
    if response.is_success:
        return
    raise error_from_response(response.status_code, response.content)


def build_httpx_kwargs(config: ClientConfig) -> dict[str, object]:
    """Shared constructor kwargs for both ``httpx.Client`` and ``AsyncClient``."""
    return {
        "base_url": config.base_url,
        "headers": config.auth_headers(),
        "timeout": config.timeout,
        # The download endpoint 302-redirects to the presigned URL; we want the
        # JSON body (with expiry), so never auto-follow.
        "follow_redirects": False,
    }
