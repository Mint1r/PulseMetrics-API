
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.core.postgres import Base
import uuid
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped,  mapped_column
from datetime import date as date2, datetime


class ReportModel(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id : Mapped[uuid.UUID]
    date : Mapped[date2]
    total_events : Mapped[int]
    unique_users : Mapped[int]
    unique_sessions : Mapped[int]
    events_by_type : Mapped[dict] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "date",
            name="uq_report_project_date",
        ),
    )