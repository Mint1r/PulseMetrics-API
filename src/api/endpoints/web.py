from fastapi.responses import FileResponse
from fastapi import Cookie, Depends
from src.core.postgres import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.security.auth import is_authenticated
from fastapi.responses import RedirectResponse
from fastapi import APIRouter
from redis.asyncio import Redis
from src.core.redis_client import get_redis

web_router = APIRouter()

@web_router.get("/dashboard/{project_id}/")
async def project_dashboard(
    session_id: str | None = Cookie(default=None),
    session_db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    user_id = await is_authenticated(
        redis = redis,
        session_id=session_id,
        session_db=session_db,
        )
    
    if not user_id:
        return RedirectResponse(
        "/users/login",
        status_code=303,
        )
    
    return FileResponse(
        "frontend/project_dashboard.html",
    )

@web_router.get("/dashboard/{project_id}/hourly")
async def hourly_dashboard(
    session_id: str | None = Cookie(default=None),
    session_db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    user_id = await is_authenticated(
        redis = redis,
        session_id=session_id,
        session_db=session_db,
        )
    
    if not user_id:
        return RedirectResponse(
        "/users/login",
        status_code=303,
        )
    
    return FileResponse(
        "frontend/hourly.html",
    )

@web_router.get("/users/registration/")
async def users_registration():
    return FileResponse(
        "frontend/registration.html",
    )

@web_router.get("/users/login/")
async def users_login():
    return FileResponse(
        "frontend/login.html",
    )

@web_router.get("/dashboard")
async def dashboard(
    session_id: str | None = Cookie(default=None),
    session_db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    ):
    user_id = await is_authenticated(
        redis = redis,
        session_id=session_id,
        session_db=session_db,
        )
    
    if not user_id:
        return RedirectResponse(
        "/users/login",
        status_code=303,
        )

    return FileResponse(
        "frontend/dashboard.html",
    )