from tests.unit.helpers import setup_registration_dependencies
from unittest.mock import AsyncMock, patch
from redis.exceptions import RedisError
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.main import app
from sqlalchemy.exc import IntegrityError

client = TestClient(app)

def test_registration(monkeypatch):

    mock_db_session, mock_redis = setup_registration_dependencies(
        monkeypatch,
    )

    with (
        patch(
            "src.api.endpoints.auth.authorization.cache_session",
            new_callable=AsyncMock,
        ) as cache_session_mock
    ):
        response = client.post(
            "/users/registration",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

    assert response.status_code == 201

    assert "session_id=" in response.headers.get("set-cookie", "")

    mock_db_session.add.assert_called()
    mock_db_session.begin.assert_called()
    cache_session_mock.assert_awaited()    

def test_registration_unique_error(monkeypatch):

    mock_db_session, mock_redis = setup_registration_dependencies(
        monkeypatch,
    )
    mock_db_session.begin.return_value.__aexit__.side_effect = IntegrityError(
        "INSERT INTO users (email) VALUES (:email)",
        {"email": "test@example.com"},
        Exception("Duplicate email"),
    )


    with (
        patch(
            "src.api.endpoints.auth.authorization.cache_session",
            new_callable=AsyncMock,
        ) as cache_session_mock
    ):
        response = client.post(
            "/users/registration",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

    assert response.status_code == 409

    assert not "session_id=" in response.headers.get("set-cookie", "")

    mock_db_session.add.assert_called()
    mock_db_session.begin.assert_called()
    cache_session_mock.assert_not_awaited()    

def test_registration_redis_error(monkeypatch):

    mock_db_session, mock_redis = setup_registration_dependencies(
        monkeypatch,
    )

    with (
        patch(
            "src.api.endpoints.auth.authorization.cache_session",
            new_callable=AsyncMock,
            side_effect=RedisError("Redis unavailable"),
        ) as cache_session_mock
    ):
        response = client.post(
            "/users/registration",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

    assert response.status_code == 201

    assert "session_id=" in response.headers.get("set-cookie", "")

    mock_db_session.add.assert_called()
    mock_db_session.begin.assert_called()
    cache_session_mock.assert_awaited()

