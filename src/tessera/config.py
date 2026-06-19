"""Client configuration and shared request helpers (transport-agnostic)."""

from __future__ import annotations

import os
import random
from dataclasses import dataclass, field

from ._version import __version__
from .errors import ConfigurationError

__all__ = ["DEFAULT_BASE_URL", "USER_AGENT", "ClientConfig"]

DEFAULT_BASE_URL = "https://tesseralytics.dev"
API_KEY_ENV_VAR = "TESSERA_API_KEY"
USER_AGENT = f"tessera-python/{__version__}"

# Statuses worth retrying: rate limiting + transient server/gateway errors.
RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


def resolve_api_key(api_key: str | None) -> str:
    """Resolve the API key from the argument, then ``$TESSERA_API_KEY``."""
    key = api_key or os.environ.get(API_KEY_ENV_VAR)
    if not key:
        raise ConfigurationError(
            "No API key provided. Pass api_key=... or set the "
            f"{API_KEY_ENV_VAR} environment variable. "
            "Get a free key at https://tesseralytics.dev."
        )
    return key


@dataclass(slots=True)
class ClientConfig:
    """Resolved configuration shared by the sync and async clients."""

    api_key: str = field(repr=False)
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 30.0
    max_retries: int = 3
    user_agent: str = USER_AGENT

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")

    def auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }


def backoff_delay(attempt: int, retry_after: float | None) -> float:
    """Compute the delay before a retry.

    Honours a server ``Retry-After`` when present, otherwise exponential backoff
    (0.5s, 1s, 2s, …) with full jitter to avoid thundering herds.
    """
    if retry_after is not None and retry_after >= 0:
        return retry_after
    base = 0.5 * (2**attempt)
    return random.uniform(0, base)
