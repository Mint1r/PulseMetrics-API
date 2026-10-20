from tests.unit.helpers import setup_logout_dependencies, _assert_logout_redirect
from redis.exceptions import RedisError
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_logout(monkeypatch):
    session_obj = MagicMock()
    mock_db_session, mock_redis = setup_logout_dependencies(
        monkeypatch,
        session_obj,
    )

    response = client.post(
        "/users/logout",
        headers={"Cookie": "session_id=abc"},
        follow_redirects=False,
    )

    _assert_logout_redirect(response)

    mock_db_session.execute.assert_awaited_once()
    mock_db_session.delete.assert_awaited_once_with(session_obj)
    mock_db_session.commit.assert_awaited_once()
    mock_redis.delete.assert_awaited_once()


def test_logout_without_cookie(monkeypatch):
    mock_db_session, mock_redis = setup_logout_dependencies(monkeypatch)

    response = client.post("/users/logout", follow_redirects=False)

    _assert_logout_redirect(response)

    mock_db_session.execute.assert_not_awaited()
    mock_db_session.delete.assert_not_awaited()
    mock_redis.delete.assert_not_awaited()


def test_logout_unknown_or_expired_session(monkeypatch):
    mock_db_session, mock_redis = setup_logout_dependencies(monkeypatch, None)

    response = client.post(
        "/users/logout",
        headers={"Cookie": "session_id=abc"},
        follow_redirects=False,
    )

    _assert_logout_redirect(response)

    mock_db_session.execute.assert_awaited_once()
    mock_db_session.delete.assert_not_awaited()
    mock_db_session.commit.assert_not_awaited()
    mock_redis.delete.assert_awaited_once()


def test_logout_succeeds_when_redis_unavailable(monkeypatch):
    session_obj = MagicMock()
    mock_db_session, mock_redis = setup_logout_dependencies(
        monkeypatch,
        session_obj,
    )
    mock_redis.delete.side_effect = RedisError("Redis unavailable")

    response = client.post(
        "/users/logout",
        headers={"Cookie": "session_id=abc"},
        follow_redirects=False,
    )

    _assert_logout_redirect(response)

    mock_db_session.delete.assert_awaited_once_with(session_obj)
    mock_db_session.commit.assert_awaited_once()
    mock_redis.delete.assert_awaited_once()
