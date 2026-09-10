from fastapi import FastAPI
from src.api.events import router as events_router
from src.api.registration import register_router
from src.api.analytics import router as analytic_router
from src.api.web import router as web_router
from src.core.postgres import engine
from sqladmin import Admin
from . admin.admin import ProjectAdmin, EventAdmin, ReportAdmin
from fastapi.staticfiles import StaticFiles

app = FastAPI()
admin = Admin(app, engine)

admin.add_view(ProjectAdmin)
admin.add_view(EventAdmin)
admin.add_view(ReportAdmin)

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static",
)

app.include_router(events_router)
app.include_router(register_router)
app.include_router(web_router)
app.include_router(analytic_router)

