"""Runtime AI versions exposed to the application."""

MODELS = [
    {
        "id": "baseline",
        "label": "Baseline",
        "description": "Bus-only detection with pretrained YOLO weights.",
        "enabled": True,
    },
    {
        "id": "mvp",
        "label": "MVP",
        "description": "Full transport to route_display to OCR pipeline.",
        "enabled": False,
    },
    {
        "id": "target",
        "label": "Target",
        "description": "Improved full pipeline for metric experiments.",
        "enabled": False,
    },
]


def get_enabled_models() -> list[dict[str, str]]:
    """Return only versions that are ready for selection."""
    public_models: list[dict[str, str]] = []
    for model in MODELS:
        if not model.get("enabled", False):
            continue

        public_models.append(
            {
                "id": model["id"],
                "label": model["label"],
                "description": model["description"],
            }
        )

    return public_models
