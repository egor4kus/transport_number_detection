# backend

Здесь лежит минимальный FastAPI-сервис. Backend не содержит ML-логики сам по себе: он принимает HTTP-запросы и вызывает функции из `ai/service.py`.

Текущая структура:

```text
backend/
  README.md
  __init__.py
  app.py
  requirements.txt
```

Используемая интеграция:

```python
from ai.service import list_models, predict_image
```

Текущие endpoints:

```text
GET  /health         - проверка доступности сервиса
GET  /models         - список доступных моделей
POST /predict/image  - запуск распознавания по изображению
```

Что делает backend:

```text
1. Принимает HTTP-запрос от frontend или из Swagger UI.
2. Для GET /models вызывает list_models().
3. Для POST /predict/image читает image_bytes и model_id.
4. Передает их в predict_image(image_bytes, model_id).
5. Возвращает JSON-результат от AI-слоя без дополнительного преобразования.
```

## Запуск локально

Установите зависимости AI и backend:

```bash
pip install -r ai/requirements.txt
pip install -r backend/requirements.txt
```

Поднимите сервер из корня репозитория:

```bash
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

После запуска будут доступны:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/models
```

## Как протестировать через Swagger UI

1. Откройте `http://127.0.0.1:8000/docs`.
2. Найдите `GET /models` и нажмите `Try it out`, затем `Execute`.
3. Найдите `POST /predict/image`.
4. Введите `model_id`, например `baseline`.
5. Загрузите картинку через поле `image`.
6. Нажмите `Execute` и получите JSON-ответ.

`POST /predict/image` принимает `multipart/form-data`:

```text
image    - файл изображения
model_id - строковый идентификатор модели
```

Сейчас публично доступна только модель `baseline`, потому что `mvp` и `target` в `ai/versions.py` пока выключены.


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

Backend возвращает:

```text
400 - пустой файл, битое изображение или неизвестный model_id
500 - отсутствуют веса модели или нужные Python-пакеты
```

## Замечание по архитектуре

Предполагается, что `backend/` и `ai/` живут в одном окружении или в одном Docker-контейнере. Поэтому backend импортирует AI-слой напрямую как обычный Python-модуль, без отдельного сетевого запроса между ними.
