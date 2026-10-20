from fastapi.testclient import TestClient
from src.main import app
import pytest
client = TestClient(app)
from sqlalchemy import select
from src.domain.models.user import UserModel
from src.domain.models.session import SessionModel
from src.api.security.session import hash_session
from redis.exceptions import RedisError
import src.api.endpoints.auth.authorization as auth_routes
from tests.integration.helpers import create_test_user, get_session_token

@pytest.mark.asyncio
async def test_user_registration_success(
    auth_client,
    db_session,
):
    email = "new@example.com"
    password = "TestPassword123!"

    response = await auth_client.post(
        "/users/registration",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == email
    assert data["created_at"] is not None
    assert data["id"] is not None

    cookie_header = response.headers.get("set-cookie", "")
    assert "session_id=" in cookie_header
    assert "httponly" in cookie_header.lower()
    assert "secure" in cookie_header.lower()
    assert "samesite=lax" in cookie_header.lower()

    session_token = get_session_token(response)
    assert session_token is not None

    result = await db_session.execute(
        select(UserModel).where(
            UserModel.email == email
        )
    )
    user = result.scalar_one_or_none()

    assert user is not None
    assert user.password_hash != password

    result = await db_session.execute(
        select(SessionModel).where(
            SessionModel.token_hash == hash_session(session_token)
        )
    )
    session_obj = result.scalar_one_or_none()

    assert session_obj is not None
    assert session_obj.user_id == user.id


@pytest.mark.asyncio
async def test_user_registration_duplicate_email(
    auth_client,
    db_session,
):
    email = "existing@example.com"

    existing_user = await create_test_user(
        db_session,
        email=email,
        password="ExistingPassword123!",
    )

    response = await auth_client.post(
        "/users/registration",
        json={
            "email": email,
            "password": "AnotherPassword123!",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Пользователь с таким email уже существует"
    )

    result = await db_session.execute(
        select(UserModel).where(
            UserModel.email == email
        )
    )
    users = result.scalars().all()

    assert len(users) == 1
    assert users[0].id == existing_user.id

    result = await db_session.execute(
        select(SessionModel).where(
            SessionModel.user_id == existing_user.id
        )
    )

    assert result.scalar_one_or_none() is None

@pytest.mark.asyncio
async def test_user_registration_succeeds_when_redis_fails(
    auth_client,
    db_session,
    monkeypatch,
):
    email = "redis-failure@example.com"
    password = "TestPassword123!"

    async def fail_cache_session(**kwargs):
        raise RedisError("Redis is unavailable")

    monkeypatch.setattr(
        auth_routes,
        "cache_session",
        fail_cache_session,
    )

    response = await auth_client.post(
        "/users/registration",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == email

    session_token = get_session_token(response)
    assert session_token is not None

    result = await db_session.execute(
        select(UserModel).where(
            UserModel.email == email
        )
    )
    user = result.scalar_one_or_none()

    assert user is not None

    result = await db_session.execute(
        select(SessionModel).where(
            SessionModel.token_hash == hash_session(session_token)
        )
    )
    session_obj = result.scalar_one_or_none()

    assert session_obj is not None
    assert session_obj.user_id == user.id
