# FastAPI Auth & Project Service

Backend-сервис на FastAPI с JWT-аутентификацией, управлением сессиями и проектами.

## Стек технологий
* **FastAPI** (Python 3.12)
* **SQLAlchemy 2.0** (Asyncio)
* **PostgreSQL**
* **Alembic**
* **Pydantic v2**
* **Docker & Docker Compose**

## Архитектура
* **Service Layer**: Бизнес-логика в выделенных сервисах.
* **Policy Pattern**: Управление правами доступа RBA).
* **Soft Delete**: Механизм отзыва токенов через `is_revoked`.
* **Optimization**: Использование `selectinload` и `joinedload` для решения проблемы N+1.

## Запуск проекта

1. Клонирование:
   ```bash
   git clone https://github.com/lasthero24102001/backendIT.git
   cd backendIT
2. Запуск проекта:
   docker-compose up
