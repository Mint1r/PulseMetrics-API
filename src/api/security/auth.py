from sqlalchemy import select,exists
from src.domain.models.session import SessionModel
from src.domain.models.access import ProjectAccessModel
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.security.session import hash_session
from datetime import datetime, timezone
from src.api.handlers import get_session_user_id, cache_session
from redis.asyncio import Redis
from redis.exceptions import RedisError
import os
from uuid import UUID

SESSION_CACHE_TTL = int(os.getenv("SESSION_CACHE_TTL", "600"))

async def is_authenticated(
    session_id: str | None,
    session_db: AsyncSession,
    redis: Redis,
) -> int | None:

    if session_id is None:
        return None

    token_hash = hash_session(session_id)

    user_id = await get_session_user_id(redis, token_hash)

    if user_id is None:
        result = await session_db.execute(
            select(SessionModel.user_id, SessionModel.expires_at).where(
                SessionModel.token_hash == token_hash,
                SessionModel.expires_at >= datetime.now(timezone.utc),
            )
        )  
        session = result.one_or_none()
        if session is not None:
            await cache_session(
                redis = redis,
                token_hash = token_hash,
                user_id = session.user_id,
                ttl = SESSION_CACHE_TTL)
            user_id = session.user_id

    return user_id

async def has_project_access(
    user_id: UUID,
    project_id: UUID,
    session_db: AsyncSession
) -> bool:
    
    result = await session_db.execute(
        select(
            exists().where(
                ProjectAccessModel.user_id == user_id,
                ProjectAccessModel.project_id == project_id,
            )
        )
    )

    has_access = result.scalar_one()

    return has_access


async def delete_session(
        session_id: str,
        session_db: AsyncSession,
        redis: Redis
)-> None:
    token_hash = hash_session(session_id)
    result = await session_db.execute(
        select(SessionModel).where(
            SessionModel.token_hash == token_hash
        )
    )

    session = result.scalar_one_or_none()

    if session is not None:
        await session_db.delete(session)
        await session_db.commit()

    try:
        await redis.delete(f"session:{token_hash}")
        
    except RedisError:
        pass





