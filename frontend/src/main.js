import { API_BASE_URL, getModels, predictImage } from "./api.js";
import { drawAnnotatedResult, formatBbox } from "./annotator.js";

const form = document.querySelector("#predict-form");
const imageInput = document.querySelector("#image-input");
const modelSelect = document.querySelector("#model-select");
const modelDescription = document.querySelector("#model-description");
const submitButton = document.querySelector("#submit-button");
const statusBanner = document.querySelector("#status-banner");
const resultMeta = document.querySelector("#result-meta");
const resultCanvas = document.querySelector("#result-canvas");
const canvasShell = document.querySelector("#canvas-shell");
const detectionsList = document.querySelector("#detections-list");
const jsonOutput = document.querySelector("#json-output");

let models = [];

function setStatus(message, type = "info") {
    statusBanner.textContent = message;
    statusBanner.className = `status-banner is-${type}`;
}

function clearStatus() {
    statusBanner.textContent = "";
    statusBanner.className = "status-banner";
}

function setLoading(isLoading) {
    submitButton.disabled = isLoading;
    imageInput.disabled = isLoading;
    modelSelect.disabled = isLoading || models.length === 0;
    submitButton.textContent = isLoading
        ? "Распознавание..."
        : "Запустить распознавание";
}

function getSelectedModel() {
    return models.find((model) => model.id === modelSelect.value) || null;
}

function updateModelDescription() {
    const selectedModel = getSelectedModel();

    if (!selectedModel) {
        modelDescription.textContent = "Нет доступных моделей.";
        return;
    }

    modelDescription.textContent = `${selectedModel.label}: ${selectedModel.description}`;
}

function renderModels(nextModels) {
    models = nextModels;
    modelSelect.innerHTML = "";

    if (models.length === 0) {
        const option = document.createElement("option");
        option.textContent = "Модели недоступны";
        option.value = "";
        modelSelect.append(option);
        modelSelect.disabled = true;
        updateModelDescription();
        return;
    }

    for (const model of models) {
        const option = document.createElement("option");
        option.value = model.id;
        option.textContent = model.label;
        modelSelect.append(option);
    }

    modelSelect.value = models[0].id;
    modelSelect.disabled = false;
    updateModelDescription();
}

function renderDetections(result) {
    detectionsList.innerHTML = "";
    const transports = result.transports || [];

    if (transports.length === 0) {
        const emptyItem = document.createElement("li");
        emptyItem.className = "empty-state";
        emptyItem.textContent = "Объекты не найдены.";
        detectionsList.append(emptyItem);
        return;
    }

    transports.forEach((transport, index) => {
        const item = document.createElement("li");
        item.className = "detection-card";

        const routeDisplays = transport.route_displays || [];
        const routeTexts = routeDisplays
            .map((entry) => entry.route_number?.text)
            .filter(Boolean);
        const routeSummary = routeTexts.length > 0 ? routeTexts.join(", ") : "нет";

        const titleRow = document.createElement("div");
        titleRow.className = "detection-title";

        const title = document.createElement("strong");
        title.textContent = `#${index + 1} ${transport.type}`;

        const confidence = document.createElement("span");
        confidence.textContent = Number(transport.confidence).toFixed(2);

        titleRow.append(title, confidence);

        const bbox = document.createElement("p");
        bbox.textContent = `bbox: ${formatBbox(transport.bbox)}`;

        const routeDisplaysCount = document.createElement("p");
        routeDisplaysCount.textContent = `route_displays: ${routeDisplays.length}`;

        const routeNumbers = document.createElement("p");
        routeNumbers.textContent = `route numbers: ${routeSummary}`;

        item.append(titleRow, bbox, routeDisplaysCount, routeNumbers);

        detectionsList.append(item);
    });
}

async function loadModels() {
    setStatus(`Подключение к backend: ${API_BASE_URL}`, "info");

    try {
        const fetchedModels = await getModels();
        renderModels(fetchedModels);
        setStatus(`Модели загружены: ${fetchedModels.length}`, "success");
    } catch (error) {
        renderModels([]);
        setStatus(`Не удалось загрузить модели: ${error.message}`, "error");
    }
}

async function handleSubmit(event) {
    event.preventDefault();
    clearStatus();

    const file = imageInput.files?.[0];
    const modelId = modelSelect.value;

    if (!file) {
        setStatus("Сначала выберите изображение.", "error");
        return;
    }

    if (!modelId) {
        setStatus("Нет выбранной модели.", "error");
        return;
    }

    setLoading(true);
    setStatus("Изображение отправлено на backend. Жду ответ...", "info");
    resultMeta.textContent = "Выполняется распознавание...";

    try {
        const result = await predictImage({ file, modelId });
        const { imageWidth, imageHeight } = await drawAnnotatedResult({
            canvas: resultCanvas,
            file,
            result,
        });

        canvasShell.classList.remove("is-empty");
        jsonOutput.textContent = JSON.stringify(result, null, 2);
        renderDetections(result);

        const transportCount = (result.transports || []).length;
        resultMeta.textContent = [
            `model=${result.model_id}`,
            `image=${imageWidth}x${imageHeight}`,
            `transports=${transportCount}`,
        ].join(" | ");

        setStatus(`Готово. Найдено объектов: ${transportCount}.`, "success");
    } catch (error) {
        resultMeta.textContent = "Запрос завершился ошибкой.";
        setStatus(`Ошибка: ${error.message}`, "error");
    } finally {
        setLoading(false);
    }
}

modelSelect.addEventListener("change", updateModelDescription);
form.addEventListener("submit", handleSubmit);

setLoading(false);
loadModels();
