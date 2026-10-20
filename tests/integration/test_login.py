from fastapi.testclient import TestClient
from src.main import app
import pytest
client = TestClient(app)
from sqlalchemy import select
from src.domain.models.user import UserModel
from src.domain.models.session import SessionModel
from src.api.security.password import hash_password
from src.api.security.session import hash_session
from http.cookies import SimpleCookie
from redis.exceptions import RedisError
import src.api.endpoints.auth.authorization as auth_routes
from tests.integration.helpers import create_test_user, get_session_token

@pytest.mark.asyncio
async def test_user_login_success(auth_client, db_session):
    user = await create_test_user(db_session)

    response = await auth_client.post(
        "/users/login",
        json={
            "email": user.email,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(user.id)
    assert data["email"] == user.email
    assert data["created_at"] is not None

    cookie_header = response.headers.get("set-cookie", "")
    cookie_header_lower = cookie_header.lower()

    assert "session_id=" in cookie_header
    assert "httponly" in cookie_header_lower
    assert "secure" in cookie_header_lower
    assert "samesite=lax" in cookie_header_lower
    assert "max-age=2592000" in cookie_header_lower

    session_token = get_session_token(response)
    assert session_token

    token_hash = hash_session(session_token)

    result = await db_session.execute(
        select(SessionModel).where(
            SessionModel.token_hash == token_hash
        )
    )
    session_obj = result.scalar_one_or_none()

    assert session_obj is not None
    assert session_obj.user.id == user.id

@pytest.mark.asyncio
async def test_user_login_unknown_email(auth_client):
    response = await auth_client.post(
        "/users/login",
        json={
            "email": "unknown@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Неверный email или пароль"
    )
    assert "session_id" not in response.headers.get("set-cookie", "")


@pytest.mark.asyncio
async def test_user_login_wrong_password(
    auth_client,
    db_session,
):
    user = await create_test_user(db_session)

    response = await auth_client.post(
        "/users/login",
        json={
            "email": user.email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Неверный email или пароль"
    )
    assert "session_id" not in response.headers.get("set-cookie", "")

    result = await db_session.execute(
        select(SessionModel).where(
            SessionModel.user == user
        )
    )

    assert result.scalar_one_or_none() is None



@pytest.mark.asyncio
async def test_user_login_succeeds_when_redis_fails(
    auth_client,
    db_session,
    monkeypatch,
):
    user = await create_test_user(db_session)

    async def fail_cache_session(**kwargs):
        raise RedisError("Redis is unavailable")

    monkeypatch.setattr(
        auth_routes,
        "cache_session",
        fail_cache_session,
    )

    response = await auth_client.post(
        "/users/login",
        json={
            "email": user.email,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == user.email
    assert get_session_token(response) is not None

    session_token = get_session_token(response)

    result = await db_session.execute(
        select(SessionModel).where(
            SessionModel.token_hash == hash_session(session_token)
        )
    )

    session_obj = result.scalar_one_or_none()

    assert session_obj is not None
    assert session_obj.user.id == user.id




