from fastapi import FastAPI
from src.api.events import router as events_router
from src.core.postgres import engine
from sqladmin import Admin

app = FastAPI()
admin = Admin(app, engine)

app.include_router(events_router)



