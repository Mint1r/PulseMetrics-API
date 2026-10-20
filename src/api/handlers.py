from redis.asyncio import Redis
from redis.exceptions import RedisError
from datetime import datetime, timezone

async def cache_session(
    redis: Redis,
    token_hash: str,
    user_id: int,
    ttl
) -> None:

    await redis.set(
        f"session:{token_hash}",
        str(user_id),
        ex = ttl
    )


async def get_session_user_id(
    redis: Redis,
    token_hash: str,
) -> int | None:
    try:
        user_id = await redis.get(f"session:{token_hash}")
        
    except RedisError:
        user_id = None

    return user_id