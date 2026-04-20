# ai

Возможная структура (AI-generated):

```text
ai/
  README.md

  models/
    detector.pt
    route_recognizer.pt

  pipeline/
    detector.py
    recognizer.py
    matcher.py
    pipeline.py

  scripts/
    train.py
    evaluate.py
    predict.py
```

Идея папки: здесь лежит весь код, связанный с компьютерным зрением и ML. Backend должен только вызывать готовый pipeline, а не знать детали обучения, распознавания и сопоставления объектов.

Минимальный ML-пайплайн:

```text
1. Получить изображение.
2. Найти на изображении транспорт:
   - bus
   - trolleybus
3. Найти область с номером маршрута:
   - route_display
4. Сопоставить route_display с конкретным транспортом.
5. Вырезать crop с номером маршрута.
6. Распознать номер маршрута через OCR или классификатор.
7. Вернуть список результатов:
   - тип транспорта
   - номер маршрута
   - bounding boxes
   - confidence
```

Baseline:

```text
Предобученная YOLO-модель ищет bus, затем OCR пытается найти номер на изображении или crop'е транспорта.
```

MVP:

```text
Дообученная YOLO-модель ищет bus / trolleybus / route_display, после чего отдельный модуль распознает номер маршрута.
```
