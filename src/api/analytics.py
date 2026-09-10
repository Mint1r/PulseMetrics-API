from fastapi import APIRouter
from fastapi.responses import FileResponse
from datetime import date, timedelta
from uuid import UUID
from redis.asyncio import Redis
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from src.core.postgres import get_db
from src.core.redis_client import get_redis
from src.domain.models.analytics import ReportModel
import json

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics"],
)


@router.get("/{project_id}/daily")
async def get_daily_reports(
    project_id: UUID,
    days: int = Query(
        default=30,
        ge=1,
        le=365,
    ),
    db: AsyncSession = Depends(get_db),
):
    start_date = date.today() - timedelta(days=days - 1)

    result = await db.execute(
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


@router.get("/{project_id}/hourly")
async def get_hourly_reports(
    project_id: UUID,
    redis: Redis = Depends(get_redis),
):
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