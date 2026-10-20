from fastapi.testclient import TestClient
from src.main import app
import pytest
client = TestClient(app)
from sqlalchemy import select
from src.domain.models.user import UserModel
from src.domain.models.session import SessionModel
from src.api.security.password import hash_password
from src.api.security.auth import cache_session
from src.api.security.session import hash_session,generate_session

@pytest.mark.asyncio
async def test_user_logout_with_active_session(
    auth_client,
    db_session,
    test_redis,
):
    user = UserModel(
        email="logout@example.com",
        password_hash=hash_password("TestPassword123!"),
    )

    db_session.add(user)

    await db_session.flush()
    user_id = user.id

    session_token = generate_session()
    token_hash = hash_session(session_token)

    session_obj = SessionModel(
        token_hash=token_hash,
        user=user,
    )

    db_session.add(session_obj)
    await db_session.commit()

    await cache_session(
        redis=test_redis,
        token_hash=token_hash,
        user_id=user_id,
        ttl=600,
    )

    redis_key = f"session:{token_hash}"

    assert await test_redis.get(redis_key) is not None

    result = await db_session.execute(
        select(SessionModel).where(
            SessionModel.token_hash == token_hash
        )
    )
    assert result.scalar_one_or_none() is not None

    response = await auth_client.post(
        "/users/logout",
        headers={
            "Cookie": f"session_id={session_token}",
        },
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/users/login"

    cookie_header = response.headers.get("set-cookie", "").lower()

    assert "session_id=" in cookie_header
    assert "max-age=0" in cookie_header

    result = await db_session.execute(
        select(SessionModel).where(
            SessionModel.token_hash == token_hash
        )
    )

    assert result.scalar_one_or_none() is None

    assert await test_redis.get(redis_key) is None

@pytest.mark.asyncio
async def test_user_logout_without_session(
    auth_client,
):
    response = await auth_client.post("/users/logout")

    assert response.status_code == 303
    assert response.headers["location"] == "/users/login"

    cookie_header = response.headers.get("set-cookie", "").lower()

    assert "session_id=" in cookie_header
    assert "max-age=0" in cookie_header