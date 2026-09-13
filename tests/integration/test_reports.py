import uuid
from datetime import datetime, timezone
from unittest.mock import patch
from src.core.postgres_test_sync import TestSessionLocal
from src.domain.models.project import ProjectModel
from src.domain.models.event import EventModel
from src.domain.models.analytics import ReportModel
from sqlalchemy import select
from src.workers.tasks import generate,generate_daily_report,generate_hour_report
from freezegun import freeze_time
import json


def test_generate(db_session_sync):

    try:
        project_id = uuid.uuid4()

        project = ProjectModel(
            id=project_id,
            title="Test project",
            api_key=f"test-{uuid.uuid4()}",
        )

        db_session_sync.add(project)

        events = [
            EventModel(
                project_id=project_id,
                event_type="page_view",
                user_id="user_1",
                session_id="session_1",
                properties={},
                timestamp=datetime(
                    2026, 8, 21, 10, 5, tzinfo=timezone.utc
                ),
            ),
            EventModel(
                project_id=project_id,
                event_type="page_view",
                user_id="user_1",
                session_id="session_1",
                properties={},
                timestamp=datetime(
                    2026, 8, 21, 10, 10, tzinfo=timezone.utc
                ),
            ),
            EventModel(
                project_id=project_id,
                event_type="purchase",
                user_id="user_2",
                session_id="session_2",
                properties={},
                timestamp=datetime(
                    2026, 8, 21, 10, 20, tzinfo=timezone.utc
                ),
            ),
            EventModel(
                project_id=project_id,
                event_type="page_view",
                user_id=None,
                session_id="session_3",
                properties={},
                timestamp=datetime(
                    2026, 8, 21, 10, 30, tzinfo=timezone.utc
                ),
            ),
        ]

        db_session_sync.add_all(events)
        db_session_sync.commit()

        start = datetime(
            2026, 8, 21, 10, 0, tzinfo=timezone.utc
        )

        end = datetime(
            2026, 8, 21, 11, 0, tzinfo=timezone.utc
        )

        with patch(
            "src.workers.tasks.SessionLocal",
            TestSessionLocal,
        ):
            result = generate(
                start=start,
                end=end,
                project_id=project_id,
            )

        assert result == {
            "project_id": str(project_id),
            "date": "2026-08-21",
            "total_events": 4,
            "unique_users": 2,
            "unique_sessions": 3,
            "events_by_type": {
                "page_view": 3,
                "purchase": 1,
            },
        }

    finally:
        db_session_sync.rollback()
        db_session_sync.close()


@freeze_time("2026-08-22 13:40:00")
def test_generate_daily_report(db_session_sync, test_redis_sync):

    project_id = uuid.uuid4()

    project = ProjectModel(
        id=project_id,
        title="Test project",
        api_key=f"test-{uuid.uuid4()}",
    )

    db_session_sync.add(project)

    events = [
        EventModel(
            project_id=project_id,
            event_type="page_view",
            user_id="user_1",
            session_id="session_1",
            properties={},
            timestamp=datetime(
                2026, 8, 21, 10, 5, tzinfo=timezone.utc
            ),
        ),
        EventModel(
            project_id=project_id,
            event_type="page_view",
            user_id="user_1",
            session_id="session_1",
            properties={},
            timestamp=datetime(
                2026, 8, 21, 10, 10, tzinfo=timezone.utc
            ),
        ),
        EventModel(
            project_id=project_id,
            event_type="purchase",
            user_id="user_2",
            session_id="session_2",
            properties={},
            timestamp=datetime(
                2026, 8, 21, 10, 20, tzinfo=timezone.utc
            ),
        ),
        EventModel(
            project_id=project_id,
            event_type="page_view",
            user_id=None,
            session_id="session_3",
            properties={},
            timestamp=datetime(
                2026, 8, 21, 10, 30, tzinfo=timezone.utc
            ),
        ),
    ]

    db_session_sync.add_all(events)
    db_session_sync.commit()

    with patch(
        "src.workers.tasks.SessionLocal",
        TestSessionLocal,
    ), patch(
        "src.workers.tasks.redis",
        test_redis_sync,
    ):
        generate_daily_report(str(project_id))

    report = db_session_sync.execute(
                select(ReportModel).where(
                    ReportModel.project_id == project_id
                )
            ).scalar_one()

            
    assert report.project_id == project_id
    assert report.date.isoformat() == "2026-08-21"

    assert report.total_events == 4
    assert report.unique_users == 2
    assert report.unique_sessions == 3

    assert report.events_by_type == {
        "page_view": 3,
        "purchase": 1,
    } 



@freeze_time("2026-08-21 11:30:00")
def test_generate_hour_report(db_session_sync,test_redis_sync):

    project_id = uuid.uuid4()

    project = ProjectModel(
        id=project_id,
        title="Test project",
        api_key=f"test-{uuid.uuid4()}",
    )

    db_session_sync.add(project)

    events = [
        EventModel(
            project_id=project_id,
            event_type="page_view",
            user_id="user_1",
            session_id="session_1",
            properties={},
            timestamp=datetime(
                2026, 8, 21, 10, 5, tzinfo=timezone.utc
            ),
        ),
        EventModel(
            project_id=project_id,
            event_type="page_view",
            user_id="user_1",
            session_id="session_1",
            properties={},
            timestamp=datetime(
                2026, 8, 21, 10, 10, tzinfo=timezone.utc
            ),
        ),
        EventModel(
            project_id=project_id,
            event_type="purchase",
            user_id="user_2",
            session_id="session_2",
            properties={},
            timestamp=datetime(
                2026, 8, 21, 10, 20, tzinfo=timezone.utc
            ),
        ),
        EventModel(
            project_id=project_id,
            event_type="page_view",
            user_id=None,
            session_id="session_3",
            properties={},
            timestamp=datetime(
                2026, 8, 21, 10, 30, tzinfo=timezone.utc
            ),
        ),
    ]

    db_session_sync.add_all(events)
    db_session_sync.commit()

    with patch(
        "src.workers.tasks.SessionLocal",
        TestSessionLocal,
    ), patch(
        "src.workers.tasks.redis",
        test_redis_sync,
    ):
        generate_hour_report(str(project_id))

    hour = "11:00"


    report = test_redis_sync.hget(
        f"hourly_reports:{project_id}:2026-08-21",
        str(hour),
    )
    report = json.loads(report)
             
    assert report["project_id"] == str(project_id)
    assert report["date"] == "2026-08-21"

    assert report["total_events"] == 4
    assert report["unique_users"] == 2
    assert report["unique_sessions"] == 3

    assert report["events_by_type"] == {
        "page_view": 3,
        "purchase": 1,
    }
