# PulseMetrics-API

Микросервис аналитики, обрабатывает события и генерирует дневные/часовые отчеты

## Features

* Приём событий через REST API
* Валидация API key (заголовок `X-API-Key`)
* Система пользователей: регистрация, вход, сессии (cookie `session_id`)
* Привязка проектов к пользователям, веб-дашборд
* Админ-панель (SQLAdmin, `/admin`)
* Redis как промежуточное хранилище
* Redis Streams
* Асинхронный consumer
* Batch-запись в PostgreSQL
* Celery для фоновых задач
* Docker Compose
* Alembic migrations
* Pytest
* Load testing

## Architecture

Данные приходят на ендпоинт, проходят через pydantic и проверку api-key (заголовок `X-API-Key`), после передаются

в редис стрим, оттуда их забирает консьюмер и батчит в бд:

Client

↓

FastAPI

↓

Redis

↓

Redis Stream

↓

Consumer

↓

PostgreSQL

## Tech Stack

* Python 3.12
* FastAPI
* PostgreSQL
* Redis
* SQLAlchemy
* Alembic
* Celery
* Docker
* Pytest
* Locust

## API Endpoints

### Events

* `POST /api/v1/events` — приём аналитических событий и добавление их в Redis Stream. Требует заголовок `X-API-Key`

### Projects

* `POST /api/v1/project-registration` — регистрация нового проекта, выдаёт `project_id` + `api_key` (ключ показывается один раз, в базе хранится только его хеш)

### Users

* `POST /users/registration` — регистрация пользователя (email + пароль), сразу создаёт сессию
* `POST /users/login` — вход, устанавливает cookie `session_id`
* `POST /users/logout` — выход, удаляет сессию и cookie
* `GET /users/dashboard/get-accesses` — список проектов, к которым у пользователя есть доступ
* `POST /users/dashboard/add-project` — добавить проект в аккаунт по `api_key`

### Analytics

* `GET /api/v1/analytics/{project_id}/daily?days=30` — дневные отчёты проекта (`days`: 1–365)
* `GET /api/v1/analytics/{project_id}/hourly` — часовые отчёты проекта

### Web

* `/users/registration/`, `/users/login/` — страницы регистрации и входа
* `/dashboard` — список проектов пользователя
* `/dashboard/{project_id}/`, `/dashboard/{project_id}/hourly` — дашборды проекта
* `/admin` — админ-панель

## Authentication

Используются два механизма:

* **API key** — для отправки событий (`POST /api/v1/events`). Передаётся в HTTP-заголовке `X-API-Key`, а не в теле запроса. Ключ выдаётся при регистрации проекта, в БД и Redis хранится его SHA-256 хеш.
* **Сессии пользователей** — для аналитики, дашбордов и управления проектами. После входа сервер ставит `HttpOnly` cookie `session_id`; в БД хранится только хеш токена, активные сессии кэшируются в Redis (`SESSION_CACHE_TTL`, по умолчанию 120 с в docker-compose). Неавторизованные запросы перенаправляются на `/users/login`.

Пользователь получает доступ к проекту, добавив его по `api_key` (`POST /users/dashboard/add-project`).

## Load Testing Results

В рамках нагрузочного тестирования входной ендпоинт показал следующие результаты:

* **RPS:** ~6,600 запросов/сек
* **Errors:** 0%
* **Median latency:** ~15 ms
* **FastAPI CPU:** ~160% (1.6 ядра)
* **Redis CPU:** ~17% 

Тест проводился с использованием Locust и был направлен на проверку производительности endpoint'а при высокой интенсивности входящих запросов.

При нагрузке около **6,600 RPS** сервис продолжал обрабатывать запросы без ошибок, при этом медианная задержка составляла около **15 ms**.

Основная нагрузка приходилась на FastAPI, потребление CPU достигало примерно **160%** 

В ходе тестирования события успешно проходили весь pipeline обработки и сохранялись в базе данных.


## Installation

Клонировать репозиторий:

```bash
git clone <repository-url>
cd <project-directory>
```

Запустить основной Docker Compose:

```bash
docker compose up --build
```

После запуска приложение и необходимые сервисы будут запущены через Docker Compose.

## Database Migrations

Миграции базы данных выполняются автоматически при запуске основного Docker Compose.

## Testing

Для тестирования используется отдельный Docker Compose, содержащий тестовые PostgreSQL и Redis.

Перед запуском тестовой инфраструктуры убедитесь, что у вас запущен основной Docker Compose.

Запуск тестовой инфраструктуры:

```bash
docker compose -f docker-compose.test.yml up -d
```

После запуска тестовых сервисов тесты можно запустить внутри FastAPI-контейнера:

```bash
docker compose exec fastapi pytest
```

Тестовая база данных использует отдельные настройки и не взаимодействует с основной базой данных.

## Test Database

Для тестовой среды используется отдельная PostgreSQL база:

и отдельный Redis.

Тестовые подключения используют переменные окружения, поэтому `alembic.ini` не требуется изменять вручную при переключении между основной и тестовой базой данных.

## Load Testing

Для нагрузочного тестирования используется Locust.

Запуск:

```bash
locust -f load_tests/locustfile.py
```

После запуска Locust предоставляет web-интерфейс для настройки количества пользователей и нагрузки.

В рамках нагрузочного тестирования проверяется производительность API endpoint'ов и обработка большого количества входящих событий.

## API

Основной endpoint принимает события и помещает их в Redis Stream для дальнейшей асинхронной обработки.

Пример запроса:

```http
POST /api/v1/events
X-API-Key: <api_key>
Content-Type: application/json

{
  "project_id": "9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c",
  "event_type": "page_view",
  "user_id": "usr_12345",
  "session_id": "sess_abc123xyz",
  "properties": {"page": "/home"}
}
```

После успешной валидации событие помещается в Redis Stream и возвращается ответ о принятии события.

## Background Processing

Обработка событий выполняется асинхронно.

Consumer читает сообщения из Redis Stream, собирает их в batch и записывает в PostgreSQL.

Celery используется для выполнения фоновых задач и формирования аналитических отчетов.

## Reports

Сервис формирует аналитические отчёты:

* дневные отчёты
* часовые отчёты

Отчёты формируются на основе данных, сохранённых в PostgreSQL.

## Docker

Проект использует Docker Compose для запуска инфраструктуры.

Основной Compose содержит сервисы приложения и production/development инфраструктуру.

Тестовый Compose используется для отдельной PostgreSQL базы и Redis, предназначенных для интеграционных тестов.

## Configuration

Конфигурация подключения к PostgreSQL, Redis и другим сервисам передаётся через environment variables.

Для разных окружений используются разные значения подключения.

## Development

Основная разработка выполняется внутри Docker-контейнеров.

Для просмотра логов:

```bash
docker compose logs -f
```

Для входа в FastAPI-контейнер:

```bash
docker compose exec fastapi bash
```

## Performance

Проект также тестируется под нагрузкой с использованием Locust.

Нагрузочное тестирование используется для оценки:

* RPS
* latency
* процент ошибок
* стабильности обработки большого количества событий
* нагрузки на FastAPI, Redis и PostgreSQL
