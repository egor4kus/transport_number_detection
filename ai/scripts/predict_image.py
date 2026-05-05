"""Run a local image through one of the fixed AI versions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai.service import list_models, predict_image_path
from ai.utils.draw import save_annotated_image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local inference with one of the fixed AI versions."
    )
    parser.add_argument("--image", help="Path to the input image.")
    parser.add_argument(
        "--model-id",
        default="baseline",
        help="One of: baseline, mvp, target. Default: baseline.",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Print available runtime models and exit.",
    )
    parser.add_argument(
        "--output-image",
        help=(
            "Path for the annotated output image. "
            "Default: ai/outputs/<input_stem>_<model_id>.jpg"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list_models:
        print(json.dumps(list_models(), ensure_ascii=False, indent=2))
        return 0

    if not args.image:
        raise SystemExit("--image is required unless --list-models is used.")

    image_path = Path(args.image)
    result = predict_image_path(image_path, model_id=args.model_id)
    output_image_path = _resolve_output_image_path(
        input_image_path=image_path,
        model_id=args.model_id,
        output_image=args.output_image,
    )
    save_annotated_image(
        input_image_path=image_path,
        output_image_path=output_image_path,
        result=result,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\nAnnotated image saved to: {output_image_path}")
    return 0


def _resolve_output_image_path(
    input_image_path: Path,
    model_id: str,
    output_image: str | None,
) -> Path:
    if output_image:
        return Path(output_image)
    return Path("ai/outputs") / f"{input_image_path.stem}_{model_id}.jpg"


if __name__ == "__main__":
    raise SystemExit(main())
