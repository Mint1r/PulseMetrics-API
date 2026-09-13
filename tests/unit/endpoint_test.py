from fastapi.testclient import TestClient
from src.main import app
from src.core.redis_client import get_redis
from unittest.mock import AsyncMock
import hashlib

def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()

client = TestClient(app)

class FakeRedis:

    def __init__(self):
        self.messages = []

    async def xadd(self, name, fields):
        self.messages.append({
            "name": name,
            "fields": fields
        })
        return "fake-message-id"
        
    async def hget(self, name, fields):
        return hash_api_key('pm_dF8kP2xQ7mN4vL9sK3zY0aBcDeFgHiJkLmNoPqRsTuV')
        
def test_ingest_event():

    fake_redis = FakeRedis()

    app.dependency_overrides[get_redis] = lambda: fake_redis

    try:
        response = client.post(
            "/api/v1/events",
                    json={
                "project_id": "9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c",
                "api_key": "pm_dF8kP2xQ7mN4vL9sK3zY0aBcDeFgHiJkLmNoPqRsTuV",
                "event_type": "cart_item_added",
                "session_id": "sess_abc123xyz"
            }
        )

        assert response.status_code == 202

        data = response.json()

        assert "event_id" in data
        assert len(fake_redis.messages) == 1
        assert data["status"] == "queued"
    finally:
        app.dependency_overrides.clear()


def test_ingest_event_no_project_id():

    response = client.post(
        "/api/v1/events",
                json={
            "event_type": "cart_item_added",
            "session_id": "sess_abc123xyz"
        }
    )

    assert response.status_code == 422

    data = response.json()
    assert data['detail'][0]['type'] == 'missing'

def test_ingest_event_invalid_project_id():

    response = client.post(
        "/api/v1/events",
                json={
            "project_id": "9f8e7d6c-5b4a-3f2e",
            "api_key": "pm_dF8kP2xQ7mN4vL9sK3zY0aBcDeFgHiJkLmNoPqRsTuV",
            "event_type": "cart_item_added",
            "session_id": "sess_abc123xyz"
        }
    )

    assert response.status_code == 422
    
    data = response.json()
    assert data['detail'][0]['type'] == 'uuid_parsing'

def test_ingest_event_invalid_short_session():

    response = client.post(
        "/api/v1/events",
                json={
            "project_id": "9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c",
            "api_key": "pm_dF8kP2xQ7mN4vL9sK3zY0aBcDeFgHiJkLmNoPqRsTuV",
            "event_type": "cart_item_added",
            "session_id": "sess"
        }
    )

    assert response.status_code == 422
    
    data = response.json()
    assert data['detail'][0]['type'] == 'string_too_short'

