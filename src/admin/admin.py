from sqladmin import ModelView
from src.domain.models.project import ProjectModel
from src.domain.models.event import EventModel
from src.domain.models.analytics import ReportModel

class ProjectAdmin(ModelView, model=ProjectModel):
    column_list = [
        ProjectModel.id,
        ProjectModel.title,
        ProjectModel.api_key,
        ProjectModel.created_at,
    ]

class EventAdmin(ModelView, model=EventModel):
    column_list = [
        EventModel.id,
        EventModel.project_id,
        EventModel.event_type,
        EventModel.user_id,
        EventModel.session_id,
        EventModel.properties,
        EventModel.timestamp,
    ]


class ReportAdmin(ModelView, model=ReportModel):
    column_list = [
        ReportModel.id,
        ReportModel.project_id,
        ReportModel.date,
        ReportModel.total_events,
        ReportModel.unique_users,
        ReportModel.unique_sessions,
        ReportModel.events_by_type,
        ReportModel.created_at,
    ]
