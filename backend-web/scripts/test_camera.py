"""Fetch a single frame from a NYC DOT camera and run inference.

Usage:
    python scripts/test_camera.py Grand_St_Bowery
    python scripts/test_camera.py <address>  [--save frame.jpg]

The address must be a key from frontend-web/app/data/cameras.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402
from app.inference import OpenParkingDetector  # noqa: E402


def resolve_status(value) -> str:
    if value is True:
        return "OPEN PARKING DETECTED (True)"
    if value is False:
        return "No open parking — spots occupied (False)"
    return "Indeterminate — no recognized detections (None)"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("address")
    parser.add_argument("--save", help="Write the fetched frame to this path")
    parser.add_argument(
        "--save-annotated",
        help="Write the annotated frame (bounding boxes) to this path if status is True",
    )
    args = parser.parse_args()

    settings = get_settings()

    with settings.resolved_cameras_path().open("r", encoding="utf-8") as f:
        cameras = json.load(f)

    record = cameras.get(args.address)
    if record is None:
        raise SystemExit(
            f"Unknown address {args.address!r}. "
            f"Check {settings.resolved_cameras_path()} for valid keys."
        )
    camera_id = record["camera_id"]

    url = f"{settings.dot_image_base.rstrip('/')}/{camera_id}/image"
    params = {"t": int(time.time() * 1000)}
    print(f"Fetching {url}")
    resp = httpx.get(url, params=params, timeout=settings.dot_request_timeout_seconds)
    resp.raise_for_status()
    image_bytes = resp.content
    print(f"Got {len(image_bytes)} bytes")

    if args.save:
        Path(args.save).write_bytes(image_bytes)
        print(f"Saved frame to {args.save}")

    detector = OpenParkingDetector(settings)
    detector.load()
    status, annotated_bytes = detector.predict(image_bytes)
    print()
    print(f"Status: {resolve_status(status)}")
    if annotated_bytes is not None:
        print(f"Annotated frame: {len(annotated_bytes)} bytes")
        if args.save_annotated:
            Path(args.save_annotated).write_bytes(annotated_bytes)
            print(f"Saved annotated frame to {args.save_annotated}")


if __name__ == "__main__":
    main()
