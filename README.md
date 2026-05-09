# transport_number_detection

team_members:\
Микерин Егор\
Мостовой Сергей\
Карпов Михаил

## Структура

- `ai/` — ML-логика и веса модели.
- `backend/` — FastAPI-сервис, прослойка между frontend и ai.
- `frontend/` — простой веб-интерфейс для загрузки изображения и показа рамок.

## Запуск вручную

Установите зависимости:

```bash
pip install -r ai/requirements.txt
pip install -r backend/requirements.txt
```

Поднимите backend в одном терминале:

```bash
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Поднимите frontend во втором терминале:

```bash
cd frontend
python3 -m http.server 3000
```

Откройте:

```text
http://127.0.0.1:3000
```

В этом режиме:

- frontend работает на `127.0.0.1:3000`
- backend работает на `127.0.0.1:8000`
- docs backend доступны на `http://127.0.0.1:8000/docs`

Подробнее:
- [backend/README.md](/Users/egor4kus/PetProjects/transport_number_detection/backend/README.md)
- [frontend/README.md](/Users/egor4kus/PetProjects/transport_number_detection/frontend/README.md)
- [ai/README.md](/Users/egor4kus/PetProjects/transport_number_detection/ai/README.md)

## Запуск через Docker Compose

Собрать и запустить:

```bash
docker compose up --build
```

Собрать и запустить в фоне:

```bash
docker compose up --build -d
```

Остановить контейнеры без удаления:

```bash
docker compose stop
```

Снова запустить остановленные контейнеры:

```bash
docker compose start
```

Остановить и удалить контейнеры проекта:

```bash
docker compose down
```

Запуск с другим внешним портом frontend:

```bash
FRONTEND_PORT=8088 docker compose up --build -d
```

В этом режиме:

- frontend по умолчанию доступен на `http://127.0.0.1:8080`
- docs backend доступны на `http://127.0.0.1:8080/docs`
- backend отдельно наружу не публикуется
- backend-образ собирается с CPU-only PyTorch

Подробнее:
- [backend/README.md](/Users/egor4kus/PetProjects/transport_number_detection/backend/README.md)
- [frontend/README.md](/Users/egor4kus/PetProjects/transport_number_detection/frontend/README.md)
