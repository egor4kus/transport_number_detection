"""Minimal FastAPI backend for transport number detection."""

from __future__ import annotations
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from ai.service import list_models, predict_image


app = FastAPI(title="Transport Number Detection API")


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple success response for uptime checks."""
    return {"status": "ok"}


@app.get("/models")
def get_models() -> list[dict[str, str]]:
    """Expose the enabled model versions from the AI layer."""
    return list_models()


@app.post("/predict/image")
async def predict_image_endpoint(
    image: UploadFile = File(...),
    model_id: str = Form(...),
) -> dict[str, object]:
    """Accept an image upload and run the selected AI pipeline."""
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image is empty.",
        )

    try:
        return predict_image(image_bytes=image_bytes, model_id=model_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except (FileNotFoundError, RuntimeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
