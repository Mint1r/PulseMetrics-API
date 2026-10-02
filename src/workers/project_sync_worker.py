import asyncio
from redis.exceptions import RedisError

from src.core.redis_client import redis
from src.sync_projects_to_redis import sync_projects_to_redis


async def run():
    redis_available = False

    while True:
        try:
            await redis.ping()

            if not redis_available:
                redis_available = True

                if not await redis.exists("projects-data"):
                    await sync_projects_to_redis()

        except RedisError:
            redis_available = False

        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run())