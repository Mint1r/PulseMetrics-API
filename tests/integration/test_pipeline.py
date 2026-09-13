from fastapi.testclient import TestClient
from src.main import app
from src.consumers.consumer import process_events
from src.core.postgres_test import AsyncSessionLocal as AsyncSessionLocal_test
from src.core.redis_client import get_redis
from src.domain.models.event import EventModel
from src.domain.models.project import ProjectModel
from sqlalchemy import select
client = TestClient(app)
from unittest.mock import patch
import httpx, uuid, secrets, hashlib, pytest
def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()

@pytest.mark.asyncio
async def test_pipeline(test_redis,db_session):
    async def override_get_redis():
        yield test_redis
        
    app.dependency_overrides[get_redis] = override_get_redis

    project_id = uuid.uuid4()
    api_key = secrets.token_urlsafe(32)

    project = ProjectModel(
        id=project_id,
        title="Test project",
        api_key=hash_api_key(api_key),
    )

    await test_redis.hset('projects-data',str(project_id),hash_api_key(api_key))

    db_session.add(project)
    await db_session.commit()

    try:
        transport = httpx.ASGITransport(app=app)

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:

            response = await client.post(
                "/api/v1/events",
                json={
                    "project_id": str(project_id),
                    "api_key": api_key,
                    "event_type": "cart_item_added",
                    "session_id": "sess_abc123xyz",
                },
            )

        assert response.status_code == 202
        
        messages = await test_redis.xrange('events_stream')

        assert len(messages) == 1

        reids_id, data = messages[0]

        assert 'event_id' in data
        assert 'data' in data

        events = [
            (reids_id,data)
        ]

        with patch(
                "src.consumers.consumer.AsyncSessionLocal",
                AsyncSessionLocal_test
            ):

            await process_events(events=events,redis=test_redis)

        result = await db_session.execute(select(EventModel).where(EventModel.project_id == str(project_id)))
        event = result.scalar_one()

        assert event.event_type == 'cart_item_added'
        assert event.session_id == 'sess_abc123xyz'

    finally:
        app.dependency_overrides.clear()






