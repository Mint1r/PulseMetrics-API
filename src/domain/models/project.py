from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from src.core.postgres import Base
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime


class ProjectModel(Base):

    __tablename__ = "projects"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    title : Mapped[str] = mapped_column(String(64),index=True)
    api_key :  Mapped[str] = mapped_column(unique=True)
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )
    events : Mapped[list["EventModel"]] = relationship(
        back_populates="project",
    )


