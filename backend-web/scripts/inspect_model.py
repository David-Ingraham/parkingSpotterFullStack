"""Print the class-index -> label map embedded in the YOLO weights.

Usage:
    python scripts/inspect_model.py              # uses WEIGHTS_PATH from .env
    python scripts/inspect_model.py ../weights.pt
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402


def main() -> None:
    settings = get_settings()
    weights = Path(sys.argv[1]) if len(sys.argv) > 1 else settings.resolved_weights_path()
    if not weights.exists():
        raise SystemExit(f"Weights not found at {weights}")

    from ultralytics import YOLO

    model = YOLO(str(weights))
    names = getattr(model, "names", None) or {}
    if isinstance(names, list):
        names = {i: n for i, n in enumerate(names)}

    print(f"Weights: {weights}")
    print("Classes:")
    for idx in sorted(names, key=lambda k: int(k)):
        print(f"  {idx}: {names[idx]}")

    configured_open = settings.open_classes
    configured_occupied = settings.occupied_classes
    print()
    print(f"OPEN_CLASSES (from env):     {configured_open}")
    print(f"OCCUPIED_CLASSES (from env): {configured_occupied}")

    labels = {str(v).lower() for v in names.values()}
    missing = [c for c in (configured_open + configured_occupied) if c.lower() not in labels]
    if missing:
        print(f"WARNING: not present in model: {missing}")
    else:
        print("All configured class names are present in the model.")


if __name__ == "__main__":
    main()
