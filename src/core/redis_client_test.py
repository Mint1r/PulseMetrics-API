from redis.asyncio import Redis
from typing import AsyncGenerator
from redis import Redis as Redis_sync
from . config import REDIS_URL_TEST as REDIS_URL


redis = Redis.from_url(REDIS_URL, decode_responses=True) 
async def get_redis() -> AsyncGenerator[Redis,None]:
    client = Redis.from_url(REDIS_URL, decode_responses=True) 
    try: 
        yield client
    finally:
        await client.aclose()
sync_redis = Redis_sync.from_url(REDIS_URL, decode_responses=True) 