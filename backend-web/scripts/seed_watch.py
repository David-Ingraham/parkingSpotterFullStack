"""End-to-end smoke test for POST /watch.

Usage:
    python scripts/seed_watch.py Grand_St_Bowery you@example.com 30
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("Usage: seed_watch.py <address> <email> <minutes>")
    address, email, minutes = sys.argv[1], sys.argv[2], int(sys.argv[3])

    settings = get_settings()
    base = os.environ.get("WATCHER_BASE_URL", "http://localhost:8080")

    resp = httpx.post(
        f"{base.rstrip('/')}/watch",
        headers={"X-API-Key": settings.shared_api_key},
        json={"address": address, "email": email, "minutes": minutes},
        timeout=10,
    )
    print(f"HTTP {resp.status_code}")
    print(resp.text)

    state = httpx.get(
        f"{base.rstrip('/')}/state/{address}",
        headers={"X-API-Key": settings.shared_api_key},
        timeout=10,
    )
    print()
    print(f"GET /state/{address}: HTTP {state.status_code}")
    print(state.text)


if __name__ == "__main__":
    main()
