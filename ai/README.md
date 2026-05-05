# ai

Идея папки: здесь лежит весь AI-слой проекта. Для учебного проекта структура сделана простой и читаемой: есть три явных версии `baseline`, `mvp`, `target`, и для каждой версии предусмотрен свой Python-пайплайн.

Текущая структура:

```text
ai/
  README.md
  __init__.py
  requirements.txt

  service.py
  versions.py

  models/
    baseline/
      bus_detector.pt
    mvp/
    target/

  pipelines/
    __init__.py
    baseline.py
    mvp.py
    target.py

  utils/
    __init__.py
    image.py
    draw.py
    ocr.py

  scripts/
    __init__.py
    predict_image.py
```

Ключевые идеи:

- `service.py` является точкой входа в AI-компонент.
- `versions.py` хранит список доступных версий для интерфейса и backend.
- `pipelines/` содержит три явных пайплайна: `baseline`, `mvp`, `target`.
- `models/` хранит веса по версиям.
- `utils/` содержит небольшие вспомогательные функции для изображений, отрисовки и OCR.
- `scripts/` нужны для локального запуска.

Минимальный AI-поток:

```text
1. Получить изображение.
2. По model_id выбрать один из трех пайплайнов.
3. Запустить соответствующую Python-функцию.
4. Выполнить inference.
5. Вернуть тип транспорта, номер маршрута, bbox и confidence.
```

Формат ответа:

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

Разметка датасета для обучения:

```text
Один датасет в формате YOLO

Классы:
0 - bus
1 - trolleybus
2 - route_display
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

Runtime-версии:

```text
baseline - готовая YOLO-модель для детекции автобусов
mvp      - полный пайплайн transport -> route_display -> OCR
target   - улучшенная версия полного пайплайна для экспериментов
```

Сейчас реализован только `baseline`, поэтому в `GET /models` и в локальном `--list-models` должна показываться только эта версия. `mvp` и `target` остаются в коде как следующие шаги, но ещё не должны предлагаться пользователю.

Как работает baseline:

```text
1. Backend или локальный скрипт передает изображение в ai/service.py.
2. service.py загружает изображение и исправляет EXIF-ориентацию.
3. По model_id="baseline" вызывается pipelines/baseline.py.
4. Baseline загружает готовые YOLO-веса из ai/models/baseline/bus_detector.pt.
5. YOLO запускается с фильтром classes=[5], то есть ищет только class "bus".
6. На выходе формируется JSON с image.width, image.height и списком transports.
7. Локальный скрипт дополнительно сохраняет картинку с рамками в ai/outputs/.
```
