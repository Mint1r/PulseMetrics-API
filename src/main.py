from fastapi import FastAPI
from src.api.endpoints.events import api_router
from src.api.endpoints.project_registration import api_router as api_router2
from src.api.endpoints.auth.analytics import analytics_router
from src.api.endpoints.auth.authorization import auth_router
from src.api.endpoints.auth.dashboard import dashboard_router
from src.api.endpoints.web import web_router
from src.core.postgres import engine
from sqladmin import Admin
from src.admin.admin import ProjectAdmin, EventAdmin, ReportAdmin
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from src.core.redis_client import redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis.aclose()


app = FastAPI(lifespan=lifespan)
admin = Admin(app, engine)

admin.add_view(ProjectAdmin)
admin.add_view(EventAdmin)
admin.add_view(ReportAdmin)

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static",
)

app.include_router(api_router)
app.include_router(api_router2)
app.include_router(analytics_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(web_router)


