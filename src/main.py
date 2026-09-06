from fastapi import FastAPI
from src.api.events import router as events_router
from src.api.registration import register_router
from src.core.postgres import engine
from sqladmin import Admin
from . admin.admin import ProjectAdmin, EventAdmin

app = FastAPI()
admin = Admin(app, engine)

app.include_router(events_router)
app.include_router(register_router)

admin.add_view(ProjectAdmin)
admin.add_view(EventAdmin)

