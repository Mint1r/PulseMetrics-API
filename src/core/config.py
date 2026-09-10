DATABASE_URL = "postgresql+asyncpg://pulse_root:root@db:5432/pulse_db"
DATABASE_URL_SYNC = "postgresql+psycopg://pulse_root:root@db:5432/pulse_db"

REDIS_URL = "redis://redis:6379/0"

CELERY_BROKER = "redis://redis:6379/1"
CELERY_BACKEND = "redis://redis:6379/2"