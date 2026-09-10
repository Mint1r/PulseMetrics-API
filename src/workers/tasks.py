from . celery_app import app
from src.core.postgres_sync import SessionLocal
from src.domain.models.project import ProjectModel
from src.domain.models.event import EventModel
from src.domain.models.analytics import ReportModel
from sqlalchemy import select
from src.core.redis_client import sync_redis as redis
from sqlalchemy import select, func, distinct
from datetime import datetime, timedelta, timezone
import json
from sqlalchemy.dialects.postgresql import insert

@app.task
def generate_daily_reports():
    (_dispatch_daily_reports())


def _dispatch_daily_reports():
    with SessionLocal() as session:
        project_ids = (session.scalars(
            select(ProjectModel.id)
        )).all()

        for project_id in project_ids:
            generate_daily_report.delay(str(project_id))

@app.task
def generate_daily_report(project_id: str):

    now = datetime.now(timezone.utc)
    date = now.date().isoformat()

    end = datetime.now(timezone.utc).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    start = end - timedelta(days=1)

    report = generate(end=end,start=start,project_id=project_id)
    _set_report(report=report)

    redis.delete(
    f"hourly_reports:{project_id}:{date}"
    )


@app.task
def generate_hour_reports():
    (_dispatch_hour_reports())


def _dispatch_hour_reports():
    with SessionLocal() as session:
        project_ids = (session.scalars(
            select(ProjectModel.id)
        )).all()

        for project_id in project_ids:
            generate_hour_report.delay(str(project_id))

@app.task
def generate_hour_report(project_id: str):
    now = datetime.now(timezone.utc)
    hour = now.strftime("%H:00")
    date = now.date().isoformat()

    end = datetime.now(timezone.utc).replace(
        minute=0,
        second=0,
        microsecond=0,
    )
    start = end - timedelta(hours=1)

    report = generate(end=end,start=start,project_id=project_id)

    key = (
        f"hourly_reports:"
        f"{project_id}:"
        f"{str(date)}"
    )

    redis.hset(key,str(hour),
               json.dumps(report,default=str))


def generate(end,start,project_id: str):

    with SessionLocal() as session:

        total_events = session.scalar(
            select(func.count(EventModel.id))
            .where(
                EventModel.project_id == project_id,
                EventModel.timestamp >= start,
                EventModel.timestamp < end,
            )
        )

        unique_users = session.scalar(
            select(func.count(distinct(EventModel.user_id)))
            .where(
                EventModel.project_id == project_id,
                EventModel.timestamp >= start,
                EventModel.timestamp < end,
                EventModel.user_id.is_not(None),
            )
        )

        unique_sessions = session.scalar(
            select(func.count(distinct(EventModel.session_id)))
            .where(
                EventModel.project_id == project_id,
                EventModel.timestamp >= start,
                EventModel.timestamp < end,
            )
        )

        result = session.execute(
            select(
                EventModel.event_type,
                func.count(EventModel.id),
            )
            .where(
                EventModel.project_id == project_id,
                EventModel.timestamp >= start,
                EventModel.timestamp < end,
            )
            .group_by(EventModel.event_type)
        )

        events_by_type = {
            event_type: count
            for event_type, count in result.all()
        }

        return {
            "project_id": str(project_id),
            "date": str(start.date()),
            "total_events": total_events or 0,
            "unique_users": unique_users or 0,
            "unique_sessions": unique_sessions or 0,
            "events_by_type": events_by_type,
        }

def _set_report(report):
    with SessionLocal() as session:

        stmt = insert(ReportModel).values(**report)

        stmt = stmt.on_conflict_do_update(
            constraint="uq_report_project_date",
            set_={
                "total_events": stmt.excluded.total_events,
                "unique_users": stmt.excluded.unique_users,
                "unique_sessions": stmt.excluded.unique_sessions,
                "events_by_type": stmt.excluded.events_by_type,
            },
        )

        session.execute(stmt)
        session.commit()

