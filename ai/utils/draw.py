"""Drawing helpers for annotated predictions."""

from __future__ import annotations

from pathlib import Path

from ai.utils.image import load_image_from_path

MIN_LINE_WIDTH = 4
LINE_WIDTH_RATIO = 0.003
MIN_FONT_SIZE = 28
FONT_SIZE_RATIO = 0.03
TEXT_PADDING_X = 8
TEXT_PADDING_Y = 4
TEXT_MARGIN = 6


def save_annotated_image(input_image_path, output_image_path, result):
    """Save an output image with transport and route display boxes."""
    try:
        from PIL import ImageDraw
    except ImportError as exc:
        raise RuntimeError(
            "The 'Pillow' package is required to save annotated images."
        ) from exc

    image = load_image_from_path(input_image_path)
    draw = ImageDraw.Draw(image)
    font = _load_font(image.width, image.height)
    line_width = _resolve_line_width(image.width, image.height)

    for transport in result.get("transports", []):
        transport_bbox = transport["bbox"]
        transport_label = transport["type"]
        transport_confidence = float(transport["confidence"])
        _draw_box_with_label(
            draw=draw,
            bbox=transport_bbox,
            text=f"{transport_label} {transport_confidence:.2f}",
            color="red",
            font=font,
            line_width=line_width,
            image_height=image.height,
        )

        for route_display in transport.get("route_displays", []):
            route_number = route_display.get("route_number")
            route_text = "route_display"
            if route_number and route_number.get("text"):
                route_text = f"{route_text} {route_number['text']}"

            route_confidence = float(route_display["confidence"])
            _draw_box_with_label(
                draw=draw,
                bbox=route_display["bbox"],
                text=f"{route_text} {route_confidence:.2f}",
                color="blue",
                font=font,
                line_width=line_width,
                image_height=image.height,
            )

    output_path = Path(output_image_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def _draw_box_with_label(
    draw,
    bbox,
    text: str,
    color: str,
    font,
    line_width: int,
    image_height: int,
) -> None:
    box = (
        float(bbox["x1"]),
        float(bbox["y1"]),
        float(bbox["x2"]),
        float(bbox["y2"]),
    )

    draw.rectangle(box, outline=color, width=line_width)

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_left, text_top, text_right, text_bottom = text_bbox
    text_width = text_right - text_left
    text_height = text_bottom - text_top
    label_x = box[0]
    label_y = max(0, box[1] - text_height - (2 * TEXT_PADDING_Y) - TEXT_MARGIN)
    if label_y == 0:
        label_y = min(image_height, box[1] + TEXT_MARGIN)

    background = (
        label_x,
        label_y,
        label_x + text_width + (2 * TEXT_PADDING_X),
        label_y + text_height + (2 * TEXT_PADDING_Y),
    )
    draw.rectangle(background, fill=color)
    draw.text(
        (
            label_x + TEXT_PADDING_X - text_left,
            label_y + TEXT_PADDING_Y - text_top,
        ),
        text,
        fill="white",
        font=font,
    )


def _resolve_line_width(image_width: int, image_height: int) -> int:
    return max(MIN_LINE_WIDTH, int(min(image_width, image_height) * LINE_WIDTH_RATIO))


def _load_font(image_width: int, image_height: int):
    try:
        from PIL import ImageFont
    except ImportError as exc:
        raise RuntimeError(
            "The 'Pillow' package is required to draw text labels."
        ) from exc

    font_size = max(MIN_FONT_SIZE, int(min(image_width, image_height) * FONT_SIZE_RATIO))
    for font_path in _font_candidates():
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size=font_size)
            except OSError:
                continue

    return ImageFont.load_default()


def _font_candidates() -> list[Path]:
    return [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Verdana Bold.ttf"),
        Path("/System/Library/Fonts/HelveticaNeue.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
    ]
