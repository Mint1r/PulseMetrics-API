from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from unittest.mock import AsyncMock

from src.main import app
from src.core.redis_client import get_redis
from src.core.postgres import get_db
from src.domain.models.user import UserModel


def create_test_user():
    user_obj = UserModel()

    user_obj.id = uuid4()
    user_obj.email = "test@example.com"
    user_obj.password_hash = "hashed_password"
    user_obj.created_at = datetime.now(timezone.utc)

    return user_obj


def setup_login_dependencies(monkeypatch, user_obj):
    mock_redis = AsyncMock()

    mock_db_session = MagicMock()
    mock_db_session.execute = AsyncMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.add = MagicMock()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user_obj

    mock_db_session.execute.return_value = result_mock

    monkeypatch.setitem(
        app.dependency_overrides,
        get_db,
        lambda: mock_db_session,
    )

    monkeypatch.setitem(
        app.dependency_overrides,
        get_redis,
        lambda: mock_redis,
    )

    return mock_db_session, mock_redis

def set_model_defaults(obj):
    if isinstance(obj, UserModel):
        obj.id = uuid4()
        obj.created_at = datetime.now(timezone.utc)

def setup_registration_dependencies(monkeypatch):
    mock_redis = AsyncMock()

    mock_db_session = MagicMock()
    mock_db_session.begin = MagicMock()
    mock_db_session.add = MagicMock()
    mock_db_session.add.side_effect = set_model_defaults

    monkeypatch.setitem(
        app.dependency_overrides,
        get_db,
        lambda: mock_db_session,
    )

    monkeypatch.setitem(
        app.dependency_overrides,
        get_redis,
        lambda: mock_redis,
    )

    return mock_db_session, mock_redis


def setup_logout_dependencies(monkeypatch, session_obj=None):
    mock_redis = AsyncMock()

    mock_db_session = MagicMock()
    mock_db_session.execute = AsyncMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.delete = AsyncMock()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = session_obj
    mock_db_session.execute.return_value = result_mock

    monkeypatch.setitem(app.dependency_overrides, get_db, lambda: mock_db_session)
    monkeypatch.setitem(app.dependency_overrides, get_redis, lambda: mock_redis)

    return mock_db_session, mock_redis



def _assert_logout_redirect(response):
    assert response.status_code == 303
    assert response.headers["location"] == "/users/login"

    set_cookie = response.headers.get("set-cookie", "")
    assert "session_id=" in set_cookie
    assert "Max-Age=0" in set_cookie
