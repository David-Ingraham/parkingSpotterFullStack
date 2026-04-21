from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional

import httpx

from .cameras import display_name
from .config import Settings
from .db import Database
from .inference import OpenParkingDetector
from .notifier import send_open_parking_email

logger = logging.getLogger(__name__)


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

            image_bytes = await self._fetch_image(client, camera_id)
            if image_bytes is None:
                continue

            new_status = await asyncio.to_thread(self._detector.predict, image_bytes)
            if new_status is None:
                continue

            status_changed = prev_status != new_status
            await self._db.record_check(address, new_status, status_changed)

            if new_status is True:
                await self._notify_open(address)

    async def _fetch_image(self, client: httpx.AsyncClient, camera_id: str) -> Optional[bytes]:
        url = f"{self._settings.dot_image_base.rstrip('/')}/{camera_id}/image"
        params = {"t": int(time.time() * 1000)}
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.content
        except Exception as exc:
            logger.warning("DOT fetch failed for %s: %s", camera_id, exc)
            return None

    async def _notify_open(self, address: str) -> None:
        pending = await self._db.pending_notifications(address)
        if not pending:
            return

        display = display_name(self._settings.resolved_cameras_path(), address)
        notified_ids: list[int] = []

        for row in pending:
            ok = await send_open_parking_email(
                self._settings,
                to_email=row["email"],
                address=address,
                display=display,
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
