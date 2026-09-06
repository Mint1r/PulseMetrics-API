import asyncio
from sqlalchemy import select
from src.core.postgres import AsyncSessionLocal
from src.core.redis_client import redis
from src.domain.models.project import ProjectModel
from src.domain.models.event import EventModel

REDIS_HASH = "projects-data"


async def sync_projects_to_redis():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ProjectModel.id, ProjectModel.api_key)
        )

        projects = result.all()

        if not projects:
            print("Проекты не найдены")
            return

        data = {
            str(project_id): api_key
            for project_id, api_key in projects
        }

        await redis.hset(
            REDIS_HASH,
            mapping=data,
        )

        print(f"Синхронизировано проектов: {len(data)}")


if __name__ == "__main__":
    asyncio.run(sync_projects_to_redis())