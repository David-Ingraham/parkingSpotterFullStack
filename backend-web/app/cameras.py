from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional


_Loaded = Dict[str, dict]


@lru_cache(maxsize=1)
def _load(path_str: str) -> _Loaded:
    path = Path(path_str)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if isinstance(v, dict) and "camera_id" in v}


def get_camera(path: Path, address: str) -> Optional[dict]:
    return _load(str(path)).get(address)


def display_name(path: Path, address: str) -> str:
    record = get_camera(path, address)
    if record and record.get("formatted_address"):
        return str(record["formatted_address"]).strip()
    return address.replace("_", " ")
