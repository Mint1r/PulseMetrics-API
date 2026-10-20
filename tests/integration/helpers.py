
from fastapi.testclient import TestClient
from src.main import app
client = TestClient(app)
from src.domain.models.user import UserModel
from src.api.security.password import hash_password
from http.cookies import SimpleCookie


async def create_test_user(
    db_session,
    email="test@example.com",
    password="TestPassword123!",
):
    user = UserModel(
        email=email,
        password_hash=hash_password(password),
    )

    db_session.add(user)
    await db_session.commit()

    return user


def get_session_token(response):
    cookies = SimpleCookie()
    cookies.load(response.headers.get("set-cookie", ""))

    if "session_id" not in cookies:
        return None

    return cookies["session_id"].value
