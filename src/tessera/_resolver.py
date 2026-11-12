"""Concurrent presigned-URL resolution.

Each ``(asset, coin, month)`` partition needs its own short-lived presigned URL,
minted via the download endpoint. For multi-partition reads we resolve them
concurrently — a thread pool for the sync client, ``asyncio.gather`` for async.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from concurrent.futures import ThreadPoolExecutor

from .models import PartitionRef

ResolvedPartition = tuple[PartitionRef, list[str]]

_MAX_WORKERS = 8


def resolve_sync(
    fetch_urls: Callable[[PartitionRef], list[str]],
    refs: Sequence[PartitionRef],
) -> list[ResolvedPartition]:
    """Resolve presigned URLs for ``refs`` concurrently, preserving order."""
    if len(refs) == 1:
        ref = refs[0]
        return [(ref, fetch_urls(ref))]
    workers = min(_MAX_WORKERS, len(refs))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        urls = list(pool.map(fetch_urls, refs))
    return list(zip(refs, urls, strict=True))


async def resolve_async(
    fetch_urls: Callable[[PartitionRef], Awaitable[list[str]]],
    refs: Sequence[PartitionRef],
) -> list[ResolvedPartition]:
    """Resolve presigned URLs for ``refs`` concurrently, preserving order."""
    urls = await asyncio.gather(*(fetch_urls(ref) for ref in refs))
    return list(zip(refs, urls, strict=True))
