from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image

from .config import Settings

logger = logging.getLogger(__name__)


class OpenParkingDetector:
    """Wraps a YOLOv8/v12 model loaded via ultralytics.

    The trained model has two classes: `open_parking` and `parked_cars`.
    `predict` returns a tuple `(status, annotated_jpeg_bytes)`:
      - status True  : at least one `open_parking` detection above threshold.
      - status False : no `open_parking`, but at least one `parked_cars`.
                       Interpretation: the block is full.
      - status None  : no recognized detections. Frame is too dark / occluded
                       / noisy to trust; skip this cycle.

    `annotated_jpeg_bytes` is populated when status is True or False. It contains
    the input frame with bounding boxes, class labels, and confidences drawn
    by ultralytics' `Results.plot()`. On any failure to render or encode, the
    second element is None and callers should fall back to the raw frame.

    The exact label strings are driven by OPEN_CLASSES and OCCUPIED_CLASSES
    in config so they can be re-mapped without touching this file."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._model = None
        self._class_names: dict[int, str] = {}

    def load(self) -> None:
        weights = self._settings.resolved_weights_path()
        if not weights.exists():
            raise FileNotFoundError(f"YOLO weights not found at {weights}")

        from ultralytics import YOLO

        logger.info("Loading YOLO weights from %s", weights)
        model = YOLO(str(weights))
        names = getattr(model, "names", None) or {}
        if isinstance(names, list):
            names = {i: n for i, n in enumerate(names)}
        self._model = model
        self._class_names = {int(k): str(v) for k, v in names.items()}
        logger.info("YOLO classes: %s", self._class_names)

        configured = {c.lower() for c in self._settings.open_classes} | {
            c.lower() for c in self._settings.occupied_classes
        }
        loaded = {v.lower() for v in self._class_names.values()}
        missing = configured - loaded
        if missing:
            logger.warning(
                "Configured class names %s not present in model classes %s. "
                "Predictions will likely all be None.",
                sorted(missing),
                sorted(loaded),
            )

    def predict(self, image_bytes: bytes) -> Tuple[Optional[bool], Optional[bytes]]:
        if self._model is None:
            raise RuntimeError("Detector has not been loaded")

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as exc:
            logger.warning("Could not decode image: %s", exc)
            return None, None

        try:
            results = self._model.predict(
                source=image,
                conf=self._settings.inference_conf_threshold,
                verbose=False,
            )
        except Exception as exc:
            logger.exception("Inference failure: %s", exc)
            return None, None

        open_labels = {c.lower() for c in self._settings.open_classes}
        occupied_labels = {c.lower() for c in self._settings.occupied_classes}

        open_count = 0
        occupied_count = 0

        for r in results or []:
            boxes = getattr(r, "boxes", None)
            if boxes is None or len(boxes) == 0:
                continue
            cls_tensor = getattr(boxes, "cls", None)
            if cls_tensor is None:
                continue
            for raw in cls_tensor.tolist():
                label = self._class_names.get(int(raw), "").lower()
                if label in open_labels:
                    open_count += 1
                elif label in occupied_labels:
                    occupied_count += 1

        logger.debug(
            "Inference counts: open=%d occupied=%d", open_count, occupied_count
        )

        if open_count > 0 or occupied_count > 0:
            annotated = self._render_annotated(results)
            if open_count > 0:
                return True, annotated
            return False, annotated
        return None, None

    def _render_annotated(self, results) -> Optional[bytes]:
        """Encode the first result with bounding boxes as a JPEG byte string.

        Returns None on any failure; callers should fall back to the raw frame."""
        try:
            first = results[0] if results else None
            if first is None:
                return None
            bgr = first.plot()
            rgb = Image.fromarray(bgr[:, :, ::-1])
            buf = io.BytesIO()
            rgb.save(buf, format="JPEG", quality=85)
            return buf.getvalue()
        except Exception as exc:
            logger.warning("Annotated image render failed: %s", exc)
            return None
