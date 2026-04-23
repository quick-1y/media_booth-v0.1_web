# Parking Media Wall

> Цифровой медиастенд для парковок — информационный киоск на базе **FastAPI**, отображающий свободные места, тарифы, часы работы и рекламную карусель.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-0.1.0-orange)

---

## Содержание

- [Возможности](#возможности)
- [Технологии](#технологии)
- [Структура проекта](#структура-проекта)
- [Быстрый старт](#быстрый-старт)
- [Переменные окружения](#переменные-окружения)
- [Конфигурация](#конфигурация)
- [Режимы работы](#режимы-работы)
- [Меню настроек](#меню-настроек)
- [API](#api)
- [Разработка без Docker](#разработка-без-docker)
- [Архитектура](#архитектура)

---

## Возможности

| Функция | Описание |
|---|---|
| **Свободные места** | Получение данных с парковочного парсера (JSP) через backend-proxy с кешированием |
| **Часы работы** | Настраиваемые текстовые строки |
| **Тарифы** | Произвольный список тарифных условий |
| **Рекламная карусель** | Автоматическая прокрутка изображений и видео из папки `/data/ads` |
| **Режимы работы** | Ручной (`open`/`closed`) или расписание (время открытия/закрытия) |
| **Веб-панель настроек** | Редактирование `settings.yaml` прямо из браузера — без перезапуска |
| **Диагностика** | Тест подключения к парсеру, просмотр raw YAML |
| **Скрытый доступ** | Меню открывается горячими клавишами или жестом — не виден обычному посетителю |

---

## Технологии

- **Backend:** FastAPI 0.116, Uvicorn, httpx, Pydantic v2, PyYAML
- **Frontend:** Vanilla JS, Jinja2-шаблоны, CSS-переменные
- **Инфраструктура:** Docker Compose, Nginx 1.27-alpine
- **Зависимости:** Poetry, Python ≥ 3.11

---

## Структура проекта

```text
.
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── health.py       # GET /api/health
│   │   │   ├── media.py        # GET /api/media/list
│   │   │   ├── parking.py      # GET /api/parking/status, POST /api/parking/test
│   │   │   └── settings.py     # GET/POST /api/settings
│   │   └── router.py
│   ├── core/
│   ├── route/                  # HTML-страницы (Jinja2)
│   ├── schemas/                # Pydantic-модели конфига
│   ├── services/               # Бизнес-логика (parking, media, settings)
│   ├── web/
│   │   ├── static/
│   │   │   ├── css/styles.css
│   │   │   └── js/
│   │   └── templates/
│   └── main.py
├── config/
│   └── settings.yaml           # Основной конфиг (монтируется в контейнер)
├── data/
│   └── ads/                    # Рекламные материалы (jpg, png, mp4, …)
├── nginx/
│   └── default.conf
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── .env.example
```

---

## Быстрый старт

### Требования

- Docker ≥ 24 и Docker Compose plugin **или** Python 3.11+

### Запуск через Docker (рекомендуется)

```bash
# 1. Создать файл переменных окружения
cp .env.example .env

# 2. Собрать образ и запустить
docker compose up -d --build

# 3. Открыть в браузере
open http://localhost:8085
```

```bash
# Остановить
docker compose down
```

### Обновление

```bash
docker compose pull
docker compose up -d --build
```

---

## Переменные окружения

Файл `.env` (создаётся из `.env.example`):

| Переменная | По умолчанию | Описание |
|---|---|---|
| `NGINX_PORT` | `8085` | Внешний порт Nginx |
| `APP_CONFIG_PATH` | `/app/config/settings.yaml` | Путь к файлу конфигурации внутри контейнера |
| `APP_LOG_LEVEL` | `info` | Уровень логирования Uvicorn (`debug`, `info`, `warning`, `error`) |

---

## Конфигурация

Все настройки хранятся в `config/settings.yaml`. Файл монтируется в контейнер как volume — изменения применяются без пересборки образа. Редактировать можно вручную **или** через встроенную веб-панель.

<details>
<summary>Полная схема <code>settings.yaml</code></summary>

```yaml
version: 1

app:
  locale: ru-RU              # Локаль для форматирования дат/чисел
  timezone: Europe/Moscow    # Таймзона часов на экране
  show_clock: false          # Показывать/скрывать часы
  clock_format: HH:mm        # Формат отображения времени

parking:
  parser:
    server: http://host:port       # Базовый URL JSP-парсера
    path: /pgs/map_monitor/parking_free_public.jsp
    token: <token>                 # Токен авторизации (добавляется как ?token=)

content:
  working_hours:
    - "Ежедневно: 08:00–22:00"    # Произвольные строки
  tariffs:
    - "Первые 2 часа бесплатно"
    - "С 3-го часа — 50 рублей/час"

media:
  ads_path: /data/ads              # Путь к папке с рекламными файлами
  carousel_seconds: 8              # Время показа одного слайда (сек)
  allowed_extensions:              # Поддерживаемые форматы
    - .jpg
    - .jpeg
    - .png
    - .webp
    - .gif
    - .mp4
    - .webm
    - .ogg

ui:
  settings_access:
    hidden_hotspot_enabled: true   # Скрытая кнопка в углу экрана
  diagnostics:
    show_raw_yaml_preview: true
    show_parser_test: true
  blocks:
    show_working_hours: true
    show_free_spaces: true
    show_tariffs: true
    show_carousel: true

appearance:
  accent_color: "#ffffff"
  success_color: "#00ff33"
  warning_color: "#ff0000"
  danger_color: "#a81600"
  background_start: "#ff7e05"    # Цвет начала градиента фона
  background_end: "#fd238a"      # Цвет конца градиента фона

operating_mode:
  manual_mode: closed            # open | closed | auto
  schedule_enabled: false
  schedule_from: "10:00"
  schedule_to: "22:00"
  closed_text: "Парковка не работает"
```

</details>

---

## Режимы работы

Управляется секцией `operating_mode` в `settings.yaml`:

| `manual_mode` | `schedule_enabled` | Поведение |
|---|---|---|
| `open` | — | Всегда показывает экран «открыто» |
| `closed` | — | Всегда показывает заглушку `closed_text` |
| `auto` | `false` | Открыто без ограничений по времени |
| `auto` | `true` | Открыто в интервале `schedule_from` – `schedule_to`, иначе — закрыто |

---

## Меню настроек

Меню скрыто от рядового пользователя и открывается тремя способами:

1. **Скрытая кнопка** — почти невидимая зона в правом верхнем углу экрана
2. **Горячие клавиши** — `Alt + Shift + S`
3. **Тач-жест** — многократный тап по заголовку страницы

### Вкладки настроек

| Вкладка | Что настраивается |
|---|---|
| **Общие** | Заголовок экрана, название локации, часы |
| **Парковка** | URL парсера, путь, токен, интервалы, TLS |
| **Контент** | Часы работы, тарифы |
| **Реклама** | Путь к папке, список файлов, время слайда |
| **Оформление** | Акцентные и фоновые цвета |
| **Диагностика** | Тест подключения к парсеру, просмотр YAML, путь к конфигу |

---

## API

Все эндпоинты доступны по префиксу `/api`. Интерактивная документация: `http://localhost:8085/docs`.

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/api/health` | Проверка работоспособности сервиса |
| `GET` | `/api/settings` | Получить текущий конфиг в JSON |
| `POST` | `/api/settings` | Обновить конфиг (записывает в `settings.yaml`) |
| `GET` | `/api/parking/status` | Статус парковки (с кешем 15 сек) |
| `POST` | `/api/parking/test` | Тест произвольного парсера (из формы диагностики) |
| `GET` | `/api/media/list` | Список медиафайлов из папки рекламы |

---

## Разработка без Docker

```bash
# Установить зависимости
poetry install

# Скопировать конфиг
cp .env.example .env

# Запустить dev-сервер
APP_CONFIG_PATH=config/settings.yaml poetry run uvicorn app.main:app --reload --port 8000
```

Приложение будет доступно на `http://localhost:8000`.

Для линтинга:

```bash
poetry run ruff check .
poetry run ruff format .
```

---

## Архитектура

### Backend proxy к парковочному парсеру

В предыдущих реализациях браузер самостоятельно обращался к `parking_free_public.jsp`. Этот подход ломается в трёх случаях:

- **CORS** — браузер блокирует cross-origin запрос к стороннему серверу
- **Mixed Content** — HTTPS-страница не может запрашивать HTTP-ресурс
- **Внутренняя сеть** — парсер доступен только из локальной сети сервера, не клиента

В текущей версии браузер общается **только с FastAPI**, а FastAPI проксирует запрос к JSP-серверу на бэкенде. Ответ нормализуется, кешируется на 15 секунд и возвращается клиенту в унифицированном формате.

```
Браузер → Nginx → FastAPI (/api/parking/status) → JSP-парсер
                      ↑
               кеш (15 сек)
```

### Обновление настроек без перезапуска

`settings.yaml` читается при каждом запросе через `SettingsService` с файловым кешем. Запись через `/api/settings` атомарна — файл сначала записывается во временный путь, затем переименовывается. Перезапуск контейнера не требуется.

---

## Лицензия

MIT © 2024–2025
