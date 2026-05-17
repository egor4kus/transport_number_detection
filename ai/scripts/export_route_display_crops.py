#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

from PIL import Image


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".JPG", ".JPEG", ".PNG", ".BMP", ".WEBP"}
ROUTE_DISPLAY_CLASS_ID = 2
DEFAULT_PADDING_RATIO = 0.10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export crops for all YOLO-labeled route_display objects from a dataset "
            "that contains 'images' and 'labels' subfolders."
        )
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Path to the dataset root that contains 'images' and 'labels'.",
    )
    parser.add_argument(
        "--output-name",
        default="tables_crops",
        help="Name of the output folder created inside the dataset root.",
    )
    parser.add_argument(
        "--padding",
        type=float,
        default=DEFAULT_PADDING_RATIO,
        help="Relative padding added around each route_display crop. Default: 0.10",
    )
    return parser.parse_args()


def ensure_dataset_layout(source_root: Path) -> tuple[Path, Path]:
    images_dir = source_root / "images"
    labels_dir = source_root / "labels"

    if not images_dir.is_dir() or not labels_dir.is_dir():
        raise SystemExit(
            "Dataset root must contain 'images' and 'labels' subfolders."
        )

    return images_dir, labels_dir


def recreate_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def collect_image_files(images_dir: Path) -> list[Path]:
    image_files = [
        path for path in sorted(images_dir.iterdir())
        if path.is_file() and path.suffix in IMAGE_SUFFIXES
    ]

    if not image_files:
        raise SystemExit("No image files were found in the source 'images' folder.")

    return image_files


def load_route_display_boxes(label_path: Path) -> list[tuple[float, float, float, float]]:
    boxes: list[tuple[float, float, float, float]] = []

    if not label_path.is_file():
        return boxes

    with label_path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) != 5:
                continue

            class_id = int(float(parts[0]))
            if class_id != ROUTE_DISPLAY_CLASS_ID:
                continue

            x_center, y_center, width, height = (float(value) for value in parts[1:])
            boxes.append((x_center, y_center, width, height))

    return boxes


def yolo_box_to_xyxy(
    x_center: float,
    y_center: float,
    width: float,
    height: float,
    image_width: int,
    image_height: int,
    padding_ratio: float,
) -> tuple[int, int, int, int]:
    box_width = width * image_width
    box_height = height * image_height
    center_x = x_center * image_width
    center_y = y_center * image_height

    pad_x = box_width * padding_ratio
    pad_y = box_height * padding_ratio

    x1 = max(0, int(round(center_x - (box_width / 2) - pad_x)))
    y1 = max(0, int(round(center_y - (box_height / 2) - pad_y)))
    x2 = min(image_width, int(round(center_x + (box_width / 2) + pad_x)))
    y2 = min(image_height, int(round(center_y + (box_height / 2) + pad_y)))

    if x2 <= x1:
        x2 = min(image_width, x1 + 1)
    if y2 <= y1:
        y2 = min(image_height, y1 + 1)

    return x1, y1, x2, y2


def main() -> None:
    args = parse_args()
    source_root = args.source.resolve()
    output_dir = (source_root / args.output_name).resolve()

    images_dir, labels_dir = ensure_dataset_layout(source_root)
    recreate_output_dir(output_dir)
    image_files = collect_image_files(images_dir)

    manifest_path = output_dir / "manifest.csv"
    saved_count = 0

    with manifest_path.open("w", encoding="utf-8", newline="") as manifest_file:
        writer = csv.writer(manifest_file)
        writer.writerow(
            [
                "crop_file",
                "source_image",
                "label_file",
                "route_display_index",
                "x1",
                "y1",
                "x2",
                "y2",
            ]
        )

        for image_path in image_files:
            label_path = labels_dir / f"{image_path.stem}.txt"
            route_display_boxes = load_route_display_boxes(label_path)

            if not route_display_boxes:
                continue

            with Image.open(image_path) as image:
                image = image.convert("RGB")
                image_width, image_height = image.size

                for index, (x_center, y_center, width, height) in enumerate(route_display_boxes, start=1):
                    x1, y1, x2, y2 = yolo_box_to_xyxy(
                        x_center=x_center,
                        y_center=y_center,
                        width=width,
                        height=height,
                        image_width=image_width,
                        image_height=image_height,
                        padding_ratio=args.padding,
                    )

                    crop = image.crop((x1, y1, x2, y2))
                    crop_name = f"{image_path.stem}__route_display_{index:02d}.jpg"
                    crop_path = output_dir / crop_name
                    crop.save(crop_path, format="JPEG", quality=95)

                    writer.writerow(
                        [
                            crop_name,
                            image_path.name,
                            label_path.name,
                            index,
                            x1,
                            y1,
                            x2,
                            y2,
                        ]
                    )
                    saved_count += 1

    print("Done.")
    print(f"Dataset root: {source_root}")
    print(f"Output crops: {output_dir}")
    print(f"Saved route_display crops: {saved_count}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
