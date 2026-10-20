from fastapi import APIRouter
from datetime import date, timedelta
from uuid import UUID
from redis.asyncio import Redis
from fastapi import APIRouter, Depends, Query, Cookie
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from src.core.postgres import get_db
from src.core.redis_client import get_redis
from src.domain.models.analytics import ReportModel
import json
from src.api.security.auth import is_authenticated, has_project_access
from fastapi.responses import RedirectResponse
from uuid import UUID

analytics_router = APIRouter(prefix = "/api/v1/analytics")

@analytics_router.get("/{project_id}/daily")
async def get_daily_reports(
    project_id: UUID,
    days: int = Query(
        default=30,
        ge=1,
        le=365,
    ),
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

    has_access = has_project_access(
        project_id=project_id,
        user_id=user_id,
        session_db=session_db
    )
    
    if not has_access:
        return RedirectResponse(
        "/dashboard",
        status_code=303,
        )

    
    start_date = date.today() - timedelta(days=days - 1)

    result = await session_db.execute(
        select(ReportModel)
        .where(
            ReportModel.project_id == project_id,
            ReportModel.date >= start_date,
        )
        .order_by(
            ReportModel.date.asc()
        )
    )

    reports = result.scalars().all()

    return {
        "reports": [
            {
                "date": report.date,
                "total_events": report.total_events,
                "unique_users": report.unique_users,
                "unique_sessions": report.unique_sessions,
                "events_by_type": report.events_by_type,
            }
            for report in reports
        ]
    }


@analytics_router.get("/{project_id}/hourly")
async def get_hourly_reports(
    project_id: UUID,
    redis: Redis = Depends(get_redis),
    session_id: str | None = Cookie(default=None),
    session_db: AsyncSession = Depends(get_db),
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

    has_access = await has_project_access(
        project_id=project_id,
        user_id=UUID(user_id),
        session_db=session_db
    )
    
    if not await has_access:
        return RedirectResponse(
        "/dashboard",
        status_code=303,
        )
    
    now = datetime.now(timezone.utc)
    date = now.date().isoformat()

    reports = await redis.hgetall(
        f"hourly_reports:{project_id}:{date}"
    )

    return {
        "reports": [
            {
                "hour": hour,
                **json.loads(report),
            }
            for hour, report in reports.items()
        ]
    }