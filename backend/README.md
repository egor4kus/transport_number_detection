# backend

Минимальный FastAPI-сервис. Backend принимает HTTP-запросы и вызывает функции из `ai/service.py`.

## Эндпоинты

- `GET /health` — проверка доступности сервиса
- `GET /models` — список доступных моделей
- `POST /predict/image` — запуск распознавания по изображению

## Запуск локально

```bash
pip install -r ai/requirements.txt
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

После запуска backend доступен на:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

При локальном запуске frontend обычно работает на `http://127.0.0.1:3000` и ходит в этот backend на `:8000`.

## Формат запроса

`POST /predict/image` принимает `multipart/form-data`:

```text
image    - файл изображения
model_id - строковый идентификатор модели
```

## Пример ответа

Для `baseline` ответ выглядит так:

```json
{
  "model_id": "baseline",
  "image": {
    "width": 3024,
    "height": 4032
  },
  "transports": [
    {
      "type": "bus",
      "confidence": 0.71,
      "bbox": {
        "x1": 1050.0,
        "y1": 1612.4,
        "x2": 1588.2,
        "y2": 2178.6
      },
      "route_displays": []
    }
  ]
}
```

## Ошибки

- `400` — пустой файл, битое изображение или неизвестный `model_id`
- `500` — отсутствуют веса модели или нужные Python-пакеты

## Docker Compose

При `docker compose` backend тоже работает на порту `8000`, но только внутри Docker-сети. Для пользователя входной адрес в этом режиме — `http://127.0.0.1:8080`, а документация backend открывается через `http://127.0.0.1:8080/docs`.
