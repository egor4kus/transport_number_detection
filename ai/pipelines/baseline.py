"""Baseline bus detection pipeline."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


BASELINE_MODEL_PATH = (
    Path(__file__).resolve().parents[1] / "models" / "baseline" / "bus_detector.pt"
)
BUS_CLASS_ID = 5
CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45


def run_baseline(image) -> dict[str, object]:
    """Detect only buses using pretrained YOLO weights."""
    model = _load_model()
    results = model.predict(
        source=image,
        conf=CONFIDENCE_THRESHOLD,
        iou=IOU_THRESHOLD,
        classes=[BUS_CLASS_ID],
        verbose=False,
    )

    transports: list[dict[str, object]] = []
    if results:
        result = results[0]
        boxes = result.boxes
        names = result.names
        if boxes is not None:
            for box in boxes:
                class_id = int(box.cls.item())
                x1, y1, x2, y2 = [float(value) for value in box.xyxy[0].tolist()]
                transports.append(
                    {
                        "type": _resolve_label(names, class_id),
                        "confidence": float(box.conf.item()),
                        "bbox": {
                            "x1": x1,
                            "y1": y1,
                            "x2": x2,
                            "y2": y2,
                        },
                        "route_displays": [],
                    }
                )

    width, height = image.size
    return {
        "model_id": "baseline",
        "image": {
            "width": width,
            "height": height,
        },
        "transports": transports,
    }


@lru_cache(maxsize=1)
def _load_model():
    _configure_ultralytics_dir()

    if not BASELINE_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Missing baseline weights: {BASELINE_MODEL_PATH}"
        )

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError(
            "The 'ultralytics' package is required for baseline inference."
        ) from exc

    return YOLO(str(BASELINE_MODEL_PATH))


def _configure_ultralytics_dir() -> None:
    settings_dir = Path(__file__).resolve().parents[1] / "tmp" / "ultralytics"
    settings_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("YOLO_CONFIG_DIR", str(settings_dir))


def _resolve_label(names, class_id: int) -> str:
    if isinstance(names, dict):
        return str(names.get(class_id, class_id))
    if isinstance(names, list) and 0 <= class_id < len(names):
        return str(names[class_id])
    return str(class_id)
