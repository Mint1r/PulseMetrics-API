
from sqlalchemy import String, DateTime, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.core.postgres import Base
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped,  mapped_column, relationship
from datetime import datetime


class EventModel(Base):
    __tablename__ = "events"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default = uuid.uuid4)
    project_id : Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    event_type : Mapped[str]= mapped_column(String(64), nullable=False, index=True)
    user_id : Mapped[str] = mapped_column(String(128), nullable=True, index=True)
    session_id : Mapped[str] = mapped_column(String(128), nullable=False)
    
    properties: Mapped[JSONB] = mapped_column(JSONB,  default=dict)
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )

    __table_args__ = (
        Index("idx_events_properties_gin", properties, postgresql_using="gin"),
    )
    project: Mapped["ProjectModel"] = relationship(
        back_populates="events",
    )
