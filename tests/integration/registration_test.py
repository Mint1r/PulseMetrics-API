from fastapi.testclient import TestClient
from src.main import app
import pytest
from src.core.redis_client import get_redis
from src.core.postgres import get_db
client = TestClient(app)
import httpx

@pytest.mark.asyncio
async def test_registraton(test_redis,db_session):
    async def override_get_redis():
        yield test_redis
    async def override_get_db():
        yield db_session        
        
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_db] = override_get_db

    title = 'test_project'

    try:
        transport = httpx.ASGITransport(app=app)

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:

            response = await client.post(
                "/api/v1/registration",
                json={
                    "title": title,
                },
            )

        assert response.status_code == 202
        
        data = response.json()

        project_id = data["project_id"]
        api_key = data["api_key"]
        
        redis_message = await test_redis.hget('projects-data',str(project_id))
        assert redis_message

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

    finally:
        app.dependency_overrides.clear()





