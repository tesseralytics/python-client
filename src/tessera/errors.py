"""Exception hierarchy for the Tessera client.

All errors raised by this library subclass :class:`TesseraError`, so a single
``except tessera.TesseraError`` catches everything. API errors additionally
carry the HTTP ``status_code`` and the machine-readable ``code`` returned by the
server (e.g. ``not_found``, ``forbidden``).
"""

from __future__ import annotations

__all__ = [
    "AuthenticationError",
    "BadRequestError",
    "ConfigurationError",
    "ForbiddenError",
    "InternalServerError",
    "MissingDependencyError",
    "NetworkError",
    "NotFoundError",
    "PresignExpiredError",
    "ServiceUnavailableError",
    "TesseraAPIError",
    "TesseraError",
    "error_from_response",
]


class TesseraError(Exception):
    """Base class for every error raised by ``tessera``."""


class ConfigurationError(TesseraError):
    """The client was misconfigured — e.g. no API key could be resolved."""


class MissingDependencyError(TesseraError):
    """An optional dependency (polars, duckdb, pandas) is required but absent."""


class NetworkError(TesseraError):
    """A network-level failure (connection/timeout) after exhausting retries."""


class PresignExpiredError(TesseraError):
    """A presigned download URL expired before the read completed.

    Presigned URLs are short-lived (~15 minutes). Call ``scan``/``read`` again to
    mint a fresh one; do not cache a :class:`polars.LazyFrame` across that window.
    """


class TesseraAPIError(TesseraError):
    """The API returned an error response.

    Attributes:
        status_code: HTTP status code of the response.
        code: Machine-readable error code from the ``{"error": ...}`` body,
            or ``None`` if the body was missing/unparseable.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class BadRequestError(TesseraAPIError):
    """400 — the request was malformed (bad coin, month format, etc.)."""


class AuthenticationError(TesseraAPIError):
    """401 — the API key is missing, invalid, or revoked."""


class ForbiddenError(TesseraAPIError):
    """403 — your plan does not grant access to this dataset or coin.

    Upgrade at https://tesseralytics.dev to unlock Pro datasets and all coins.
    """


class NotFoundError(TesseraAPIError):
    """404 — the dataset, coin, or partition does not exist."""


class ServiceUnavailableError(TesseraAPIError):
    """503 — the catalog is temporarily unavailable. Safe to retry."""


class InternalServerError(TesseraAPIError):
    """500 — an unexpected server error."""


# Map the server's machine-readable error codes to exception classes.
_CODE_TO_EXC: dict[str, type[TesseraAPIError]] = {
    "bad_request": BadRequestError,
    "unauthorized": AuthenticationError,
    "forbidden": ForbiddenError,
    "not_found": NotFoundError,
    "unavailable": ServiceUnavailableError,
    "internal": InternalServerError,
}

# Fallback mapping when the body has no recognised code.
_STATUS_TO_EXC: dict[int, type[TesseraAPIError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: ForbiddenError,
    404: NotFoundError,
    500: InternalServerError,
    502: ServiceUnavailableError,
    503: ServiceUnavailableError,
    504: ServiceUnavailableError,
}


def error_from_response(status_code: int, body: bytes | str | None) -> TesseraAPIError:
    """Build the appropriate :class:`TesseraAPIError` from a response.

    Prefers the ``{"error": "<code>"}`` body; falls back to the HTTP status.
    """
    code: str | None = None
    if body:
        text = body.decode("utf-8", "replace") if isinstance(body, bytes) else body
        try:
            import json
            from typing import cast

            parsed = json.loads(text)
            if isinstance(parsed, dict):
                raw = cast("dict[str, object]", parsed).get("error")
                code = raw if isinstance(raw, str) else None
        except ValueError:
            code = None

    exc_cls = _CODE_TO_EXC.get(code or "") or _STATUS_TO_EXC.get(status_code, TesseraAPIError)
    detail = f" ({code})" if code else ""
    message = f"Tessera API request failed with HTTP {status_code}{detail}"
    return exc_cls(message, status_code=status_code, code=code)
