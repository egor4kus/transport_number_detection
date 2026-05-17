#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SPLIT_PATTERN = ("test", "val", "val", "train", "train", "train", "train", "train", "train", "train")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Split a YOLO dataset without train/val/test into dataset/images and "
            "dataset/labels using a fixed 70:20:10 repeating pattern. "
            "Already distributed files are kept in place; only new files are added."
        )
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Path to the source folder that contains 'images' and 'labels' subfolders.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dataset"),
        help="Output dataset root. Default: ./dataset",
    )
    return parser.parse_args()


def ensure_source_layout(source_root: Path) -> tuple[Path, Path]:
    images_dir = source_root / "images"
    labels_dir = source_root / "labels"

    if not images_dir.is_dir() or not labels_dir.is_dir():
        raise SystemExit(
            "Source folder must contain 'images' and 'labels' subfolders."
        )

    return images_dir, labels_dir


def prepare_output_dirs(output_root: Path) -> dict[str, tuple[Path, Path]]:
    split_dirs: dict[str, tuple[Path, Path]] = {}

    for split in ("train", "val", "test"):
        images_dir = output_root / "images" / split
        labels_dir = output_root / "labels" / split
        images_dir.mkdir(parents=True, exist_ok=True)
        labels_dir.mkdir(parents=True, exist_ok=True)
        split_dirs[split] = (images_dir, labels_dir)

    return split_dirs


def collect_image_files(images_dir: Path) -> list[Path]:
    image_files = [
        path for path in sorted(images_dir.iterdir())
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]

    if not image_files:
        raise SystemExit("No image files were found in the source 'images' folder.")

    return image_files


def split_name_by_index(index: int) -> str:
    return SPLIT_PATTERN[index % len(SPLIT_PATTERN)]


def is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES


def collect_existing_assignments(
    split_dirs: dict[str, tuple[Path, Path]],
) -> tuple[dict[str, str], int]:
    assignments: dict[str, str] = {}

    for split, (images_dir, labels_dir) in split_dirs.items():
        for image_path in images_dir.iterdir():
            if not is_image_file(image_path):
                continue

            stem = image_path.stem
            label_path = labels_dir / f"{stem}.txt"

            if not label_path.is_file():
                raise SystemExit(
                    f"Existing split is inconsistent: missing label file for '{image_path.name}' in '{split}'."
                )

            previous_split = assignments.get(stem)
            if previous_split and previous_split != split:
                raise SystemExit(
                    f"Image stem '{stem}' is already present in multiple splits: '{previous_split}' and '{split}'."
                )

            assignments[stem] = split

    return assignments, len(assignments)


def main() -> None:
    args = parse_args()
    source_root = args.source.resolve()
    output_root = args.output.resolve()

    images_dir, labels_dir = ensure_source_layout(source_root)
    split_dirs = prepare_output_dirs(output_root)
    existing_assignments, distributed_count = collect_existing_assignments(split_dirs)
    image_files = collect_image_files(images_dir)

    added_counts = {"train": 0, "val": 0, "test": 0}
    skipped_count = 0
    missing_label_count = 0

    for image_path in image_files:
        label_path = labels_dir / f"{image_path.stem}.txt"

        if not label_path.is_file():
            missing_label_count += 1
            continue

        existing_split = existing_assignments.get(image_path.stem)
        if existing_split:
            skipped_count += 1
            continue

        split = split_name_by_index(distributed_count)
        target_images_dir, target_labels_dir = split_dirs[split]
        shutil.copy2(image_path, target_images_dir / image_path.name)
        shutil.copy2(label_path, target_labels_dir / label_path.name)
        existing_assignments[image_path.stem] = split
        distributed_count += 1
        added_counts[split] += 1

    print("Done.")
    print(f"Source: {source_root}")
    print(f"Output: {output_root}")
    print(f"Skipped already distributed images: {skipped_count}")
    print(f"Skipped images without label files: {missing_label_count}")
    for split in ("train", "val", "test"):
        total_in_split = len(list(
            path for path in split_dirs[split][0].iterdir()
            if is_image_file(path)
        ))
        print(
            f"{split}: added {added_counts[split]}, total {total_in_split} images"
        )


if __name__ == "__main__":
    main()
