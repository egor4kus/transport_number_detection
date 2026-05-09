const MIN_LINE_WIDTH = 4;
const LINE_WIDTH_RATIO = 0.003;
const MIN_FONT_SIZE = 28;
const FONT_SIZE_RATIO = 0.03;
const TEXT_PADDING_X = 8;
const TEXT_PADDING_Y = 4;
const TEXT_MARGIN = 6;
const TRANSPORT_COLOR = "#d32f2f";
const ROUTE_DISPLAY_COLOR = "#1976d2";

function formatNumber(value) {
    return Number(value).toFixed(1);
}

function resolveLineWidth(imageWidth, imageHeight) {
    return Math.max(
        MIN_LINE_WIDTH,
        Math.round(Math.min(imageWidth, imageHeight) * LINE_WIDTH_RATIO),
    );
}

function resolveFontSize(imageWidth, imageHeight) {
    return Math.max(
        MIN_FONT_SIZE,
        Math.round(Math.min(imageWidth, imageHeight) * FONT_SIZE_RATIO),
    );
}

function loadImageFromFile(file) {
    return new Promise((resolve, reject) => {
        const imageUrl = URL.createObjectURL(file);
        const image = new Image();

        image.onload = () => {
            URL.revokeObjectURL(imageUrl);
            resolve(image);
        };

        image.onerror = () => {
            URL.revokeObjectURL(imageUrl);
            reject(new Error("Failed to load the selected image in the browser."));
        };

        image.src = imageUrl;
    });
}

function drawBoxWithLabel(ctx, bbox, text, color, imageWidth, imageHeight, lineWidth, fontSize) {
    const x1 = Number(bbox.x1);
    const y1 = Number(bbox.y1);
    const x2 = Number(bbox.x2);
    const y2 = Number(bbox.y2);
    const width = x2 - x1;
    const height = y2 - y1;

    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.strokeRect(x1, y1, width, height);

    const textMetrics = ctx.measureText(text);
    const textWidth = Math.ceil(textMetrics.width);
    const textHeight = fontSize;
    const backgroundWidth = textWidth + (2 * TEXT_PADDING_X);
    const backgroundHeight = textHeight + (2 * TEXT_PADDING_Y);
    const labelX = Math.min(
        Math.max(0, x1),
        Math.max(0, imageWidth - backgroundWidth),
    );

    let labelY = y1 - backgroundHeight - TEXT_MARGIN;
    if (labelY < 0) {
        labelY = Math.min(imageHeight - backgroundHeight, y1 + TEXT_MARGIN);
    }

    ctx.fillStyle = color;
    ctx.fillRect(labelX, labelY, backgroundWidth, backgroundHeight);
    ctx.fillStyle = "#ffffff";
    ctx.fillText(
        text,
        labelX + TEXT_PADDING_X,
        labelY + (backgroundHeight / 2),
    );
}

export async function drawAnnotatedResult({ canvas, file, result }) {
    const image = await loadImageFromFile(file);
    const imageWidth = Number(result?.image?.width) || image.naturalWidth;
    const imageHeight = Number(result?.image?.height) || image.naturalHeight;
    const context = canvas.getContext("2d");

    if (!context) {
        throw new Error("Canvas is not supported in this browser.");
    }

    canvas.width = imageWidth;
    canvas.height = imageHeight;

    context.clearRect(0, 0, imageWidth, imageHeight);
    context.drawImage(image, 0, 0, imageWidth, imageHeight);

    const lineWidth = resolveLineWidth(imageWidth, imageHeight);
    const fontSize = resolveFontSize(imageWidth, imageHeight);

    context.font = `700 ${fontSize}px "Avenir Next", "Segoe UI", sans-serif`;
    context.textBaseline = "middle";

    for (const transport of result.transports || []) {
        const transportLabel = `${transport.type} ${Number(transport.confidence).toFixed(2)}`;

        drawBoxWithLabel(
            context,
            transport.bbox,
            transportLabel,
            TRANSPORT_COLOR,
            imageWidth,
            imageHeight,
            lineWidth,
            fontSize,
        );

        for (const routeDisplay of transport.route_displays || []) {
            const routeNumber = routeDisplay.route_number?.text;
            const labelPrefix = routeNumber
                ? `route_display ${routeNumber}`
                : "route_display";
            const routeLabel = `${labelPrefix} ${Number(routeDisplay.confidence).toFixed(2)}`;

            drawBoxWithLabel(
                context,
                routeDisplay.bbox,
                routeLabel,
                ROUTE_DISPLAY_COLOR,
                imageWidth,
                imageHeight,
                lineWidth,
                fontSize,
            );
        }
    }

    return {
        imageWidth,
        imageHeight,
    };
}

export function formatBbox(bbox) {
    return [
        `x1=${formatNumber(bbox.x1)}`,
        `y1=${formatNumber(bbox.y1)}`,
        `x2=${formatNumber(bbox.x2)}`,
        `y2=${formatNumber(bbox.y2)}`,
    ].join(", ");
}
