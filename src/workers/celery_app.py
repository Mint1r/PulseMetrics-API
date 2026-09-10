from celery import Celery
from celery.schedules import crontab
from src.core.config import CELERY_BACKEND, CELERY_BROKER

app = Celery(
    "api",
    broker=CELERY_BROKER,
    backend=CELERY_BACKEND,
)

app.conf.beat_schedule = {
    "generate-hourly-reports": {
        "task": "src.workers.tasks.generate_hour_reports",
        "schedule": crontab(minute=0),
    },

    "generate-daily-reports": {
        "task": "src.workers.tasks.generate_daily_reports",
        "schedule": crontab(
            minute=0,
            hour=0,
        ),
    },
}

app.conf.imports = (
    "src.workers.tasks",
)
	
