"""Image helpers used by local scripts and AI pipelines."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path


def load_image_from_bytes(image_bytes: bytes):
    """Load an image from raw bytes and fix EXIF orientation."""
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise RuntimeError("The 'Pillow' package is required for image loading.") from exc

    image = Image.open(BytesIO(image_bytes))
    image = ImageOps.exif_transpose(image)
    return image.convert("RGB")


def load_image_from_path(image_path: str | Path):
    """Load an image from a filesystem path."""
    path = Path(image_path)
    return load_image_from_bytes(path.read_bytes())
