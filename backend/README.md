# backend

Возможная структура (AI-generated):

```text
backend/
  README.md

  app.py
  schemas.py
```

Идея папки: здесь лежит FastAPI-сервис, который принимает запросы от frontend и вызывает ML-пайплайн из `ai/`.

Минимальный сценарий:

```text
1. Frontend отправляет изображение на backend.
2. Backend принимает файл через endpoint.
3. Backend вызывает AI pipeline:
   - YOLO №1
   - YOLO №2
   - OCR
4. Backend возвращает JSON с найденным транспортом, номером маршрута и координатами bbox.
```

Возможные endpoints:

```text
GET /health
POST /predict/image
POST /predict/video
```

Для MVP достаточно:

```text
GET /health
POST /predict/image
```

Пример результата:

```text
{
  "type": "bus",
  "number": "49",
  "bbox_transport": [...],
  "bbox_route_display": [...]
}
```
