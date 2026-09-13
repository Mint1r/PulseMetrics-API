from sqlalchemy import delete
from src.core.postgres_test import AsyncSessionLocal
from src.core.postgres_test_sync import TestSessionLocal
from src.domain.models.event import EventModel
from src.domain.models.project import ProjectModel
from src.domain.models.analytics import ReportModel
import pytest_asyncio
import pytest 
from redis.asyncio import Redis
from src.core.redis_client_test import sync_redis

@pytest.fixture(scope="session")
def db_session_sync():
    session = TestSessionLocal()

    try:
        session.execute(delete(EventModel))
        session.execute(delete(ReportModel))
        session.execute(delete(ProjectModel))
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