"""Simple entrypoints for switching between AI versions."""

from __future__ import annotations

from pathlib import Path

from ai.pipelines.baseline import run_baseline
from ai.pipelines.mvp import run_mvp
from ai.pipelines.target import run_target
from ai.utils.image import load_image_from_bytes
from ai.versions import get_enabled_models


def list_models() -> list[dict[str, str]]:
    """Return runtime versions available for selection."""
    return get_enabled_models()


def predict_image(image_bytes: bytes, model_id: str) -> dict[str, object]:
    """Run the selected pipeline for an input image."""
    image = load_image_from_bytes(image_bytes)

    if model_id == "baseline":
        return run_baseline(image)
    if model_id == "mvp":
        return run_mvp(image)
    if model_id == "target":
        return run_target(image)

    raise ValueError(f"Unknown model_id: {model_id}")


def predict_image_path(image_path: str | Path, model_id: str) -> dict[str, object]:
    """Convenience helper for local scripts."""
    path = Path(image_path)
    return predict_image(path.read_bytes(), model_id=model_id)
