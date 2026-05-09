const DEFAULT_BACKEND_PORT = "8000";

function resolveApiBaseUrl() {
    const metaBaseUrl = document
        .querySelector('meta[name="api-base-url"]')
        ?.content?.trim();

    if (metaBaseUrl) {
        return metaBaseUrl.replace(/\/+$/, "");
    }

    const { protocol, hostname } = window.location;

    if (protocol === "http:" || protocol === "https:") {
        return `${protocol}//${hostname || "127.0.0.1"}:${DEFAULT_BACKEND_PORT}`;
    }

    return `http://127.0.0.1:${DEFAULT_BACKEND_PORT}`;
}

export const API_BASE_URL = resolveApiBaseUrl();

async function parseJsonOrThrow(response) {
    const contentType = response.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");
    const payload = isJson ? await response.json() : null;

    if (!response.ok) {
        const message = payload?.detail || `Request failed with status ${response.status}`;
        throw new Error(message);
    }

    if (payload === null) {
        throw new Error("Backend did not return JSON.");
    }

    return payload;
}

export async function getModels() {
    const response = await fetch(`${API_BASE_URL}/models`);
    return parseJsonOrThrow(response);
}

export async function predictImage({ file, modelId }) {
    const formData = new FormData();
    formData.append("image", file);
    formData.append("model_id", modelId);

    const response = await fetch(`${API_BASE_URL}/predict/image`, {
        method: "POST",
        body: formData,
    });

    return parseJsonOrThrow(response);
}
