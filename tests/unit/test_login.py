from tests.unit.helpers import(
    create_test_user,
    setup_login_dependencies, 
                        )
from unittest.mock import AsyncMock, patch
from redis.exceptions import RedisError
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_login(monkeypatch):
    user_obj = create_test_user()

    mock_db_session, mock_redis = setup_login_dependencies(
        monkeypatch,
        user_obj,
    )

    with (
        patch(
            "src.api.endpoints.auth.authorization.verify_password",
            return_value=True,
        ) as verify_password_mock,
        patch(
            "src.api.endpoints.auth.authorization.cache_session",
            new_callable=AsyncMock,
        ) as cache_session_mock,
    ):
        response = client.post(
            "/users/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert response.json()["id"] == str(user_obj.id)
    assert response.json()["created_at"] is not None

    assert "session_id=" in response.headers.get("set-cookie", "")

    mock_db_session.execute.assert_awaited_once()
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_awaited_once()

    verify_password_mock.assert_called_once_with(
        "TestPassword123!",
        "hashed_password",
    )

    cache_session_mock.assert_awaited_once()

def test_login_no_user(monkeypatch):
    user_obj = create_test_user()

    mock_db_session, mock_redis = setup_login_dependencies(
        monkeypatch,
        None,
    )

    with (
        patch(
            "src.api.endpoints.auth.authorization.verify_password",
            return_value=True,
        ) as verify_password_mock,
        patch(
            "src.api.endpoints.auth.authorization.cache_session",
            new_callable=AsyncMock,
        ) as cache_session_mock,
    ):
        response = client.post(
            "/users/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

    assert response.status_code == 401

    assert not "session_id=" in response.headers.get("set-cookie", "")

    mock_db_session.execute.assert_awaited_once()
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_awaited()
    cache_session_mock.assert_not_awaited()    


def test_login_wrong_password(monkeypatch):
    user_obj = create_test_user()

    mock_db_session, mock_redis = setup_login_dependencies(
        monkeypatch,
        user_obj,
    )

    with (
        patch(
            "src.api.endpoints.auth.authorization.verify_password",
            return_value=False,
        ) as verify_password_mock,
        patch(
            "src.api.endpoints.auth.authorization.cache_session",
            new_callable=AsyncMock,
        ) as cache_session_mock,
    ):
        response = client.post(
            "/users/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

    assert response.status_code == 401

    assert not "session_id=" in response.headers.get("set-cookie", "")

    mock_db_session.execute.assert_awaited_once()
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_awaited()

    verify_password_mock.assert_called_once_with(
        "TestPassword123!",
        "hashed_password",
    )

    cache_session_mock.assert_not_awaited()

def test_login_succeeds_when_redis_unavailable(monkeypatch):
    user_obj = create_test_user()

    mock_db_session, mock_redis = setup_login_dependencies(
        monkeypatch,
        user_obj,
    )

    with (
        patch(
            "src.api.endpoints.auth.authorization.verify_password",
            return_value=True,
        ),
        patch(
            "src.api.endpoints.auth.authorization.cache_session",
            new_callable=AsyncMock,
            side_effect=RedisError("Redis unavailable"),
        ) as cache_session_mock,
    ):
        response = client.post(
            "/users/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

    assert response.status_code == 200
    assert "session_id=" in response.headers.get("set-cookie", "")

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_awaited_once()
    cache_session_mock.assert_awaited_once()
