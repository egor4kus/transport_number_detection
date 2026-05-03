"""Simple entrypoints for switching between AI versions."""


def list_models():
    """Return runtime versions available for selection."""
    raise NotImplementedError


def predict_image(image_bytes: bytes, model_id: str):
    """Run the selected pipeline for an input image."""
    raise NotImplementedError
