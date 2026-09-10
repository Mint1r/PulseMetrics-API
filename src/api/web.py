from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter()


@router.get("/dashboard/{project_id}/")
async def dashboard():
    return FileResponse(
        "frontend/dashboard.html",
    )

@router.get("/dashboard/{project_id}/hourly")
async def hourly_dashboard():
    return FileResponse(
        "frontend/hourly.html",
    )