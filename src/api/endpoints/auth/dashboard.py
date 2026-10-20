
from redis.asyncio import Redis
from src.core.redis_client import get_redis
from src.core.postgres import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Cookie, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.security.auth import is_authenticated
from fastapi.responses import RedirectResponse
from src.domain.models.access import ProjectAccessModel
from src.domain.models.project import ProjectModel
from src.domain.schemas.registration import AddProjectAccessSchema
from src.api.security.password import hash_api_key

dashboard_router = APIRouter(prefix = "/users/dashboard")

@dashboard_router.get("/get-accesses")
async def get_project_access(
    session_id: str | None = Cookie(default=None),
    session_db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    ):
    
    user_id = await is_authenticated(
        session_id = session_id,
        session_db = session_db,
        redis = redis,
        )
    
    if not user_id:
        return RedirectResponse(
        "/users/login",
        status_code=303,
        )

    result = await session_db.execute(
            select(ProjectAccessModel.project_id,
                   ProjectModel.title)
                    .join(
                    ProjectAccessModel.project)
                    .where(
                        ProjectAccessModel.user_id == user_id)
    )

    return [{"id": project_id, 'title': title} for project_id, title in result.all()]


@dashboard_router.post("/add-project")
async def add_project_access(
    post_data: AddProjectAccessSchema,
    session_id: str | None = Cookie(default=None),
    session_db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    ):
    
    user_id = await is_authenticated(
        session_id = session_id,
        session_db = session_db,
        redis = redis,
        )

    hashed_api_key = hash_api_key(post_data.api_key)
    
    if user_id is None:
        return RedirectResponse(
        "/users/login",
        status_code=303,
        )

    result = await session_db.execute(
            select(ProjectModel.id).where(
                ProjectModel.api_key == hashed_api_key
        )
    )
    project_id = result.scalar_one_or_none()

    if project_id is None:
        raise HTTPException(
            status_code=404,
            detail="Проект не найден",
        )


    result = await session_db.execute(
        select(ProjectAccessModel).where(
            ProjectAccessModel.user_id == user_id,
            ProjectAccessModel.project_id == project_id,
        )
    )

    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail="У вас уже есть доступ к этому проекту",
        )

    result = await session_db.execute(
        select(ProjectModel.title).where(
            ProjectModel.id == project_id
        )
    )

    project_title = result.scalar_one_or_none()

    access_obj = ProjectAccessModel(
        user_id = user_id,
        project_id = project_id,
    )

    session_db.add(access_obj)
    await session_db.commit()

    return {"id": access_obj.project_id, "title": project_title}