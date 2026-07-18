# Railway Agent

Система регистрации событий на железнодорожном вокзале с использованием локальной AI-модели (Ollama).

## Быстрый старт

### 1. Предварительные требования

- Python 3.12+
- Node.js 18+
- [Ollama](https://ollama.ai/) запущен локально или доступен по сети

### 2. Настройка окружения

```bash
cp .env.example .env
```

Откройте `.env` и укажите параметры:

| Параметр | Описание | Пример |
|---|---|---|
| `OLLAMA_URL` | URL Ollama API | `http://localhost:11434` или `http://192.168.1.100:11434` |
| `OLLAMA_MODEL` | Модель Ollama | `qwen3:27b` |
| `DATABASE_URL` | Подключение к БД | `sqlite+aiosqlite:///./railway_agent.db` |

### 3. Установка зависимостей Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

### 4. Установка зависимостей Frontend

```bash
cd frontend
npm install
```

### 5. Запуск Ollama

Убедитесь, что Ollama запущен и нужная модель загружена:

```bash
ollama pull qwen3:27b
ollama serve
```

### 6. Запуск Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

База данных создастся автоматически при первом запуске.

### 7. Запуск Frontend

```bash
cd frontend
npm run dev
```

Откройте `http://localhost:5173` в браузере.

## Запуск через Docker

Самый простой способ запустить проект:

```bash
cp .env.example .env
# Отредактируйте .env при необходимости
docker compose up --build
```

Приложение будет доступно по адресу `http://localhost`.

Убедитесь, что Ollama доступен из контейнера. На macOS и Windows используйте `host.docker.internal` в `.env`. На Linux укажите IP-адрес хоста.

| Параметр | Docker (macOS/Windows) | Docker (Linux) | Нейтив |
|---|---|---|---|
| `OLLAMA_URL` | `http://host.docker.internal:11434` | `http://<host-ip>:11434` | `http://localhost:11434` |

## API

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/api/health` | Проверка доступности |
| `POST` | `/api/events` | Добавить событие (тело: `{"text": "..."}`) |
| `GET` | `/api/events` | Получить последние 50 событий |
| `GET` | `/api/reports` | Сгенерировать Markdown-отчёт |

## Примеры использования

### Добавление события

```bash
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{"text": "Поезд №742 прибыл на 3 путь в 12:43 с задержкой 15 минут."}'
```

### Получение списка событий

```bash
curl http://localhost:8000/api/events
```

### Генерация отчёта

```bash
curl http://localhost:8000/api/reports
```

## Структура проекта

```
RailwayAgent/
├── .env.example              # Пример конфигурации
├── backend/
│   ├── main.py               # FastAPI приложение
│   ├── config.py             # Настройки из .env
│   ├── database.py           # SQLAlchemy engine, session
│   ├── models/               # Модели БД
│   │   ├── train_arrivals.py
│   │   ├── train_departures.py
│   │   ├── evacuations.py
│   │   ├── waiting_room.py
│   │   └── request_logs.py
│   ├── schemas/              # Pydantic схемы
│   │   ├── event.py
│   │   ├── log.py
│   │   └── report.py
│   ├── services/             # Бизнес-логика
│   │   ├── ollama_service.py
│   │   ├── classifier.py
│   │   ├── database_service.py
│   │   └── report_service.py
│   ├── routers/              # API роутеры
│   │   ├── events.py
│   │   └── reports.py
│   ├── prompts/              # Prompts для Ollama
│   │   ├── classify.txt
│   │   └── report.txt
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── EventInput.tsx
│   │   │   ├── EventHistory.tsx
│   │   │   └── StatusMessage.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── reports/                  # Сгенерированные отчёты
├── logs/                     # Логи
└── database/                 # Файлы БД
```

## Таблицы базы данных

### train_arrivals
| Поле | Тип | Описание |
|---|---|---|
| id | int | Первичный ключ |
| date | date | Дата записи |
| time | str | Время прибытия (HH:MM) |
| train_number | str | Номер поезда |
| platform | int | Путь |
| delay_minutes | float | Задержка в минутах |
| notes | str | Примечание |
| created_at | datetime | Время создания записи |

### train_departures
Аналогична `train_arrivals`.

### evacuations
| Поле | Тип | Описание |
|---|---|---|
| id | int | Первичный ключ |
| date | date | Дата записи |
| start_time | str | Начало (HH:MM) |
| end_time | str | Окончание (HH:MM) |
| reason | str | Причина |
| notes | str | Примечание |

### waiting_room
| Поле | Тип | Описание |
|---|---|---|
| id | int | Первичный ключ |
| date | date | Дата записи |
| visitors | int | Количество посетителей |
| notes | str | Примечание |

### request_logs
| Поле | Тип | Описание |
|---|---|---|
| id | int | Первичный ключ |
| input_text | str | Текст пользователя |
| ollama_response | str | Ответ модели |
| success | bool | Успешность обработки |
| processed_at | datetime | Время обработки |
