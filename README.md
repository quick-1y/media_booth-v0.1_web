# Media Booth Manager

Централизованная система управления цифровыми медиастендами.  
Один сервер — любое количество стендов. Каждый стенд открывается по URL с его ID.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![Version](https://img.shields.io/badge/version-0.2.0-orange)

---

## Возможности

| Функция | Описание |
|---|---|
| **Центр управления** | Создание, удаление стендов, открытие настроек прямо со страницы управления |
| **Мультистенд** | Неограниченное количество независимых стендов, каждый по URL `/booth/{id}` |
| **Свободные места** | Данные с парковочного парсера (JSP) через backend-proxy с кешированием 15 с |
| **Рекламная карусель** | Автопрокрутка изображений и видео из папки стенда |
| **Режимы работы** | Ручной (открыт/закрыт) или расписание по времени |
| **Настройки стенда** | Скрытая панель настроек с 8 вкладками, открывается кликом в углу или из центра управления |
| **Оформление** | 13 цветовых переменных, настраиваются через color picker |
| **Диагностика** | Тест парсера, просмотр конфигурации из БД |

---

## Технологии

- **Backend:** FastAPI 0.116, Uvicorn, asyncpg, httpx, Pydantic v2
- **Frontend:** Vanilla JS, Jinja2, CSS custom properties
- **База данных:** PostgreSQL 16
- **Инфраструктура:** Docker Compose, Nginx 1.27

---

## Структура проекта

```
app/
├── api/
│   ├── endpoints/
│   │   ├── booths.py       # Все эндпоинты стендов (CRUD, settings, parking, media)
│   │   └── health.py       # GET /api/health
│   └── router.py
├── pages/
│   └── router.py           # HTML-страницы: / и /booth/{id}
├── core/
│   └── config.py           # RuntimeSettings (data_dir, log_level)
├── schemas/
│   ├── booth.py            # BoothNamePayload
│   └── config.py           # AppConfig и все вложенные секции
├── services/
│   ├── booth_service.py    # CRUD стендов в БД
│   ├── settings_service.py # Чтение/запись настроек стенда (JSONB)
│   ├── parking_service.py  # Получение данных парсера с кешем
│   ├── media_service.py    # Управление медиафайлами
│   └── deps.py             # Синглтоны сервисов (lru_cache)
├── web/
│   ├── static/
│   │   ├── css/
│   │   │   ├── styles.css       # Стили стенда
│   │   │   └── management.css   # Стили центра управления
│   │   └── js/
│   │       ├── main.js          # Логика стенда
│   │       └── management.js    # Логика центра управления
│   └── templates/
│       ├── index.html       # Страница стенда
│       └── management.html  # Центр управления
├── db.py                   # Пул подключений asyncpg, миграции
└── main.py                 # FastAPI app, lifespan
```

---

## База данных

Одна таблица:

```sql
CREATE TABLE booths (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    settings   JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

Таблица создаётся автоматически при первом запуске. Настройки каждого стенда хранятся в колонке `settings` как JSONB.

---

## Медиафайлы

Каждый стенд хранит файлы в отдельной папке:

```
data/
└── booths/
    ├── 1/     # файлы стенда #1
    ├── 2/     # файлы стенда #2
    └── ...
```

Поддерживаемые форматы: `.jpg` `.jpeg` `.png` `.webp` `.gif` `.mp4` `.webm` `.ogg`

---

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build -d
```

Открыть в браузере: `http://localhost:8085`

---

## Переменные окружения

| Переменная | По умолчанию | Описание |
|---|---|---|
| `NGINX_PORT` | `8085` | Внешний порт Nginx |
| `DATABASE_URL` | `postgresql://booth:booth@postgres:5432/booth` | Строка подключения к PostgreSQL |
| `APP_DATA_DIR` | `/data` | Корневая папка для медиафайлов |
| `APP_LOG_LEVEL` | `info` | Уровень логирования uvicorn |

---

## API

### Стенды
| Метод | URL | Описание |
|---|---|---|
| `GET` | `/api/booths` | Список всех стендов |
| `POST` | `/api/booths` | Создать стенд `{"name": "..."}` |
| `PATCH` | `/api/booths/{id}` | Переименовать стенд |
| `DELETE` | `/api/booths/{id}` | Удалить стенд |

### Настройки стенда
| Метод | URL | Описание |
|---|---|---|
| `GET` | `/api/booths/{id}/settings` | Получить настройки |
| `PUT` | `/api/booths/{id}/settings` | Сохранить настройки |

### Парковка
| Метод | URL | Описание |
|---|---|---|
| `GET` | `/api/booths/{id}/parking/status` | Данные о свободных местах |
| `POST` | `/api/booths/{id}/parking/test` | Тест подключения к парсеру |

### Медиафайлы
| Метод | URL | Описание |
|---|---|---|
| `GET` | `/api/booths/{id}/media/items` | Список файлов |
| `POST` | `/api/booths/{id}/media/upload` | Загрузить файл |
| `DELETE` | `/api/booths/{id}/media/file/{name}` | Удалить файл |
| `GET` | `/api/booths/{id}/media/file/{name}` | Получить файл |

### Служебные
| Метод | URL | Описание |
|---|---|---|
| `GET` | `/api/health` | Проверка доступности |

---

## Страницы

| URL | Описание |
|---|---|
| `/` | Центр управления стендами |
| `/booth/{id}` | Экран медиастенда |
| `/booth/{id}?settings` | Экран медиастенда с авто-открытием настроек |
| `/docs` | Swagger UI |

---

## Локальная разработка без Docker

```bash
export DATABASE_URL=postgresql://booth:booth@localhost:5432/booth
export APP_DATA_DIR=./data

poetry install
uvicorn app.main:app --reload --port 8000
```
