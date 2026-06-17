from __future__ import annotations

import logging
import time
from typing import Optional

import httpx

from .config import Settings

logger = logging.getLogger(__name__)


async def fetch_dot_image(
    client: httpx.AsyncClient,
    settings: Settings,
    camera_id: str,
    cache_buster_ms: Optional[int] = None,
) -> Optional[bytes]:
    url = f"{settings.dot_image_base.rstrip('/')}/{camera_id}/image"
    params = {"t": cache_buster_ms if cache_buster_ms is not None else int(time.time() * 1000)}
    try:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.content
    except Exception as exc:
        logger.warning("DOT fetch failed for %s: %s", camera_id, exc)
        return None
