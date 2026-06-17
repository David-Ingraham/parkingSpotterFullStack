from __future__ import annotations

import asyncio
import io
import logging
import time
from datetime import datetime, timezone
from typing import Optional

import httpx
from PIL import Image, ImageDraw, ImageFont

from .cameras import display_name
from .config import Settings
from .db import Database
from .dot import fetch_dot_image
from .inference import OpenParkingDetector
from .notifier import send_open_parking_email

logger = logging.getLogger(__name__)


_CAPTION_FONT_CANDIDATES = (
    "DejaVuSans.ttf",
    "Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)


def _load_caption_font(size: int = 14) -> ImageFont.ImageFont:
    for candidate in _CAPTION_FONT_CANDIDATES:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _caption_image(image_bytes: bytes, display: str) -> bytes:
    """Overlay a display-name + UTC timestamp caption in the bottom-left.

    Returns the original bytes unchanged on any failure."""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(img)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        caption = f"{display} - {stamp}"
        font = _load_caption_font(14)
        bbox = draw.textbbox((0, 0), caption, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        pad = 6
        rect_top = img.height - text_h - pad * 2
        draw.rectangle(
            [0, rect_top, text_w + pad * 2, img.height],
            fill=(0, 0, 0),
        )
        draw.text(
            (pad, rect_top + pad - bbox[1]),
            caption,
            fill=(255, 255, 255),
            font=font,
        )
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()
    except Exception as exc:
        logger.warning("Caption overlay failed: %s", exc)
        return image_bytes


class WatcherWorker:
    def __init__(
        self,
        settings: Settings,
        db: Database,
        detector: OpenParkingDetector,
    ):
        self._settings = settings
        self._db = db
        self._detector = detector
        self._task: Optional[asyncio.Task] = None
        self._stop = asyncio.Event()

    def start(self) -> None:
        if self._task is not None:
            return
        self._stop.clear()
        self._task = asyncio.create_task(self._run(), name="watcher-worker")

    async def stop(self) -> None:
        self._stop.set()
        if self._task is not None:
            try:
                await asyncio.wait_for(self._task, timeout=10)
            except asyncio.TimeoutError:
                self._task.cancel()
            self._task = None

    async def _run(self) -> None:
        logger.info("Watcher worker started. Poll interval = %ss", self._settings.poll_interval_seconds)
        async with httpx.AsyncClient(timeout=self._settings.dot_request_timeout_seconds) as client:
            while not self._stop.is_set():
                cycle_started = time.monotonic()
                try:
                    await self._db.prune_expired()
                    await self._cycle(client)
                except Exception as exc:
                    logger.exception("Watcher cycle failed: %s", exc)

                elapsed = time.monotonic() - cycle_started
                remaining = max(0.0, self._settings.poll_interval_seconds - elapsed)
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=remaining)
                except asyncio.TimeoutError:
                    pass

        logger.info("Watcher worker stopped.")

    async def _cycle(self, client: httpx.AsyncClient) -> None:
        targets = await self._db.active_targets()
        if not targets:
            return
        logger.debug("Checking %d target(s)", len(targets))

        for row in targets:
            address = row["address"]
            camera_id = row["camera_id"]
            prev_raw = row["open_parking_status"]
            prev_status: Optional[bool] = None if prev_raw is None else bool(prev_raw)

            image_bytes = await fetch_dot_image(client, self._settings, camera_id)
            if image_bytes is None:
                continue

            new_status, annotated_bytes = await asyncio.to_thread(
                self._detector.predict, image_bytes
            )
            if new_status is None:
                continue

            status_changed = prev_status != new_status
            await self._db.record_check(address, new_status, status_changed)

            if new_status is True:
                frame_bytes = annotated_bytes or image_bytes
                await self._notify_open(address, frame_bytes)

    async def _notify_open(self, address: str, frame_bytes: Optional[bytes]) -> None:
        pending = await self._db.pending_notifications(address)
        if not pending:
            return

        display = display_name(self._settings.resolved_cameras_path(), address)

        captioned_bytes: Optional[bytes] = None
        if frame_bytes is not None:
            captioned_bytes = await asyncio.to_thread(
                _caption_image, frame_bytes, display
            )

        notified_ids: list[int] = []

        for row in pending:
            ok = await send_open_parking_email(
                self._settings,
                to_email=row["email"],
                address=address,
                display=display,
                image_bytes=captioned_bytes,
            )
            if ok:
                notified_ids.append(int(row["id"]))

        if notified_ids:
            await self._db.mark_notified(notified_ids)
            logger.info(
                "Notified %d watcher(s) for %s about open parking",
                len(notified_ids),
                address,
            )
