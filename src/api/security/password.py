import hashlib
import hmac
from uuid import UUID

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from redis.asyncio import Redis
from src.core.redis_client import get_redis
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет пароль на соответствие хешу."""
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


api_key_header = APIKeyHeader(
    name="X-API-Key",
    description="API key проекта",
)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()

async def validate_project_access(
    project_id: UUID,
    api_key: str,
    redis: Redis,
    ) -> None:

    stored_hash = await redis.hget(
        "projects-data",
        str(project_id),
    )

    if not stored_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid project credentials",
        )

    actual_hash = hash_api_key(api_key)

    if not hmac.compare_digest(stored_hash, actual_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid project credentials",
        )


async def require_project_access(
    project_id: UUID,
    api_key: str = Security(api_key_header),
    redis: Redis = Depends(get_redis),
) -> None:
    await validate_project_access(
        project_id=project_id,
        api_key=api_key,
        redis=redis,
    )
