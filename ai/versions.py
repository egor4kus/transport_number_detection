"""Runtime AI versions exposed to the application."""

MODELS = [
    {
        "id": "baseline",
        "label": "Baseline",
        "description": "Bus-only detection with pretrained YOLO weights.",
    },
    {
        "id": "mvp",
        "label": "MVP",
        "description": "Full transport to route_display to OCR pipeline.",
    },
    {
        "id": "target",
        "label": "Target",
        "description": "Improved full pipeline for metric experiments.",
    },
]
