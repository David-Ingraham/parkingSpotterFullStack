from __future__ import annotations

import asyncio
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

_SCHEMA = """
CREATE TABLE IF NOT EXISTS camera_state (
    address TEXT PRIMARY KEY,
    camera_id TEXT NOT NULL,
    open_parking_status INTEGER,
    last_checked_utc TEXT,
    last_status_change_utc TEXT
);

CREATE TABLE IF NOT EXISTS watchers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL,
    email TEXT NOT NULL,
    requested_minutes INTEGER NOT NULL,
    created_at_utc TEXT NOT NULL,
    expires_at_utc TEXT NOT NULL,
    notified_on_current_status INTEGER NOT NULL DEFAULT 0,
    UNIQUE(address, email)
);

CREATE INDEX IF NOT EXISTS idx_watchers_address ON watchers(address);
CREATE INDEX IF NOT EXISTS idx_watchers_expires ON watchers(expires_at_utc);
"""


def _iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Database:
    """SQLite wrapper. All write paths are serialized through an asyncio.Lock
    because sqlite3 allows concurrent reads but not concurrent writers on the
    same connection."""

    def __init__(self, path: Path):
        self._path = path
        self._lock = asyncio.Lock()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path, isolation_level=None, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    @contextmanager
    def _cursor(self):
        conn = self._connect()
        try:
            cur = conn.cursor()
            yield cur
        finally:
            conn.close()

    def initialize(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._cursor() as cur:
            cur.executescript(_SCHEMA)

    async def upsert_watcher(
        self,
        address: str,
        camera_id: str,
        email: str,
        minutes: int,
    ) -> tuple[str, int]:
        """Insert or refresh a watcher row. Returns (expires_at_iso, watcher_count_for_address)."""
        def _work() -> tuple[str, int]:
            now = _utcnow()
            expires = now + timedelta(minutes=minutes)
            now_iso = _iso_utc(now)
            expires_iso = _iso_utc(expires)
            with self._cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO camera_state (address, camera_id)
                    VALUES (?, ?)
                    ON CONFLICT(address) DO UPDATE SET camera_id=excluded.camera_id
                    """,
                    (address, camera_id),
                )
                cur.execute(
                    """
                    INSERT INTO watchers (
                        address, email, requested_minutes,
                        created_at_utc, expires_at_utc, notified_on_current_status
                    )
                    VALUES (?, ?, ?, ?, ?, 0)
                    ON CONFLICT(address, email) DO UPDATE SET
                        requested_minutes=excluded.requested_minutes,
                        expires_at_utc=excluded.expires_at_utc,
                        notified_on_current_status=0
                    """,
                    (address, email.lower(), minutes, now_iso, expires_iso),
                )
                cur.execute(
                    "SELECT COUNT(*) AS n FROM watchers WHERE address=? AND expires_at_utc > ?",
                    (address, now_iso),
                )
                count = int(cur.fetchone()["n"])
            return expires_iso, count

        async with self._lock:
            return await asyncio.to_thread(_work)

    async def delete_watcher(self, address: str, email: str) -> int:
        def _work() -> int:
            with self._cursor() as cur:
                cur.execute(
                    "DELETE FROM watchers WHERE address=? AND email=?",
                    (address, email.lower()),
                )
                return cur.rowcount

        async with self._lock:
            return await asyncio.to_thread(_work)

    async def prune_expired(self) -> int:
        def _work() -> int:
            with self._cursor() as cur:
                cur.execute(
                    "DELETE FROM watchers WHERE expires_at_utc <= ?",
                    (_iso_utc(_utcnow()),),
                )
                return cur.rowcount

        async with self._lock:
            return await asyncio.to_thread(_work)

    async def active_targets(self) -> list[sqlite3.Row]:
        """Returns camera_state rows that currently have at least one non-expired watcher."""
        def _work() -> list[sqlite3.Row]:
            with self._cursor() as cur:
                cur.execute(
                    """
                    SELECT cs.address, cs.camera_id, cs.open_parking_status,
                           cs.last_checked_utc, cs.last_status_change_utc
                    FROM camera_state cs
                    WHERE EXISTS (
                        SELECT 1 FROM watchers w
                        WHERE w.address = cs.address AND w.expires_at_utc > ?
                    )
                    """,
                    (_iso_utc(_utcnow()),),
                )
                return cur.fetchall()

        return await asyncio.to_thread(_work)

    async def record_check(
        self,
        address: str,
        new_status: Optional[bool],
        status_changed: bool,
    ) -> None:
        def _work() -> None:
            now_iso = _iso_utc(_utcnow())
            value = None if new_status is None else (1 if new_status else 0)
            with self._cursor() as cur:
                if status_changed:
                    cur.execute(
                        """
                        UPDATE camera_state
                        SET open_parking_status=?, last_checked_utc=?, last_status_change_utc=?
                        WHERE address=?
                        """,
                        (value, now_iso, now_iso, address),
                    )
                    cur.execute(
                        "UPDATE watchers SET notified_on_current_status=0 WHERE address=?",
                        (address,),
                    )
                else:
                    cur.execute(
                        "UPDATE camera_state SET last_checked_utc=? WHERE address=?",
                        (now_iso, address),
                    )

        async with self._lock:
            await asyncio.to_thread(_work)

    async def pending_notifications(self, address: str) -> list[sqlite3.Row]:
        """Watchers that are non-expired and haven't been notified for the current
        status yet. Caller decides whether to actually send based on the status."""
        def _work() -> list[sqlite3.Row]:
            with self._cursor() as cur:
                cur.execute(
                    """
                    SELECT id, email, requested_minutes, expires_at_utc
                    FROM watchers
                    WHERE address=?
                      AND expires_at_utc > ?
                      AND notified_on_current_status = 0
                    """,
                    (address, _iso_utc(_utcnow())),
                )
                return cur.fetchall()

        return await asyncio.to_thread(_work)

    async def mark_notified(self, watcher_ids: Iterable[int]) -> None:
        ids = list(watcher_ids)
        if not ids:
            return

        def _work() -> None:
            placeholders = ",".join("?" for _ in ids)
            with self._cursor() as cur:
                cur.execute(
                    f"UPDATE watchers SET notified_on_current_status=1 WHERE id IN ({placeholders})",
                    ids,
                )

        async with self._lock:
            await asyncio.to_thread(_work)

    async def get_state(self, address: str) -> Optional[sqlite3.Row]:
        def _work() -> Optional[sqlite3.Row]:
            with self._cursor() as cur:
                cur.execute(
                    """
                    SELECT cs.address, cs.open_parking_status, cs.last_checked_utc,
                           (SELECT COUNT(*) FROM watchers w
                              WHERE w.address = cs.address AND w.expires_at_utc > ?) AS watcher_count
                    FROM camera_state cs
                    WHERE cs.address=?
                    """,
                    (_iso_utc(_utcnow()), address),
                )
                return cur.fetchone()

        return await asyncio.to_thread(_work)

    async def count_active_for_email(self, email: str) -> int:
        def _work() -> int:
            with self._cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) AS n FROM watchers WHERE email=? AND expires_at_utc > ?",
                    (email.lower(), _iso_utc(_utcnow())),
                )
                return int(cur.fetchone()["n"])

        return await asyncio.to_thread(_work)
