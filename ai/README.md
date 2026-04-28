# ai

Возможная структура (AI-generated):

```text
ai/
  README.md

  models/
    transport_detector.pt
    route_display_detector.pt

  pipeline/
    transport_detector.py
    route_display_detector.py
    ocr.py
    pipeline.py

  scripts/
    train_transport.py
    train_route_display.py
    evaluate.py
```

Идея папки: здесь лежит весь код, связанный с компьютерным зрением и ML. Backend должен только вызывать готовый pipeline, а не знать детали обучения, OCR и метрик.

Разметка датасета:

```text
Один датасет в формате YOLO

Классы:
0 - bus
1 - trolleybus
2 - route_display
```

Минимальный ML-пайплайн:

```text
1. Получить изображение.
2. YOLO №1 находит на изображении:
   - bus
   - trolleybus
3. Для каждого найденного транспорта сделать crop.
4. YOLO №2 ищет внутри crop:
   - route_display
5. Вырезать crop номера с небольшим padding.
6. Распознать номер маршрута через OCR.
7. Вернуть список результатов:
   - тип транспорта
   - номер маршрута
   - bounding boxes
   - confidence
```

Baseline:

```text
Предобученная YOLO-модель без дообучения ищет bus и возвращает bbox транспорта без распознавания номера маршрута.
```

MVP:

```text
YOLO №1 ищет bus / trolleybus.
YOLO №2 ищет route_display внутри crop транспорта.
OCR читает номер маршрута по crop'у табло.
```

Основные метрики:

```text
Baseline:
- AP@50 (bus)
- precision
- recall

YOLO №1:
- AP@50 (bus)
- AP@50 (trolleybus)

YOLO №2:
- AP@50 (route_display)

OCR:
- OCR accuracy

Вся система:
- End-to-end accuracy
- Latency
```
