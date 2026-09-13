# PulseMetrics-API

Микросервис аналитики, обрабатывает события и генерирует дневные/часовые отчеты

## Features

* Приём событий через REST API
* Валидация API key
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

Данные приходят на ендпоинт, проходят через pydantic и проверку api-key, после передаются

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

* `POST /api/v1/events` — приём аналитических событий и добавление их в Redis Stream

### Projects

* `POST /api/v1/registration` — регистрация новых пользователей, выдает project_id + api_key

### Analytics

* `GET /api/v1/dashboard/{project_id}/` — получение дневной аналитики проекта
* `GET /api/v1/dashboard/{project_id}/hourly` — получение дневной аналитики проекта



Для защищённых endpoint'ов используется API key.

API key передаётся в HTTP-заголовке запроса.


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
