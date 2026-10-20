from sqlalchemy import delete
from src.core.postgres_test import AsyncSessionLocal
from src.core.postgres_test_sync import TestSessionLocal
from src.domain.models.event import EventModel
from src.domain.models.project import ProjectModel
from src.domain.models.analytics import ReportModel
from src.domain.models.session import SessionModel
from src.domain.models.user import UserModel
import pytest_asyncio
import pytest 
from redis.asyncio import Redis
from src.core.redis_client_test import sync_redis
import httpx
import pytest_asyncio

from src.main import app
from src.core.postgres import get_db
from src.core.redis_client import get_redis


@pytest.fixture(scope="session")
def db_session_sync():
    session = TestSessionLocal()

    try:
        session.execute(delete(EventModel))
        session.execute(delete(ReportModel))
        session.execute(delete(ProjectModel))
        session.execute(delete(SessionModel))
        session.execute(delete(UserModel))
        session.commit()

        yield session

    finally:
        session.rollback()
        session.close()

@pytest_asyncio.fixture
async def db_session():
    session = AsyncSessionLocal()

    try:
        await session.execute(delete(EventModel))
        await session.execute(delete(ReportModel))
        await session.execute(delete(ProjectModel))
        await session.execute(delete(SessionModel))
        await session.execute(delete(UserModel))
        await session.commit()

        yield session

    finally:
        await session.rollback()
        await session.close()


@pytest_asyncio.fixture
async def test_redis():
    redis = Redis.from_url(
        "redis://test_redis:6379/0",
        decode_responses=True,
    )

    try:
        await redis.flushdb()

        yield redis

    finally:
        await redis.flushdb()
        await redis.aclose()

@pytest.fixture
def test_redis_sync():
    try:
        sync_redis.flushdb()

        yield sync_redis

    finally:
        sync_redis.flushdb()
        sync_redis.close()


@pytest_asyncio.fixture
async def auth_client(test_redis, db_session):
    original_overrides = app.dependency_overrides.copy()

    async def override_get_redis():
        yield test_redis

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = httpx.ASGITransport(app=app)

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)