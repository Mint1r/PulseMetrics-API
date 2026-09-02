from redis.asyncio import Redis
from typing import AsyncGenerator
from redis import Redis as Redis_sync
from . config import REDIS_URL

redis = Redis.from_url(REDIS_URL, decode_responses=True,max_connections=500,) 

async def get_redis() -> AsyncGenerator[Redis,None]:
    yield redis

sync_redis = Redis_sync.from_url(REDIS_URL, decode_responses=True) 

