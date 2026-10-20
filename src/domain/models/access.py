from sqlalchemy import DateTime, func
from src.core.postgres import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

class ProjectAccessModel(Base):
    __tablename__ = "project_access"

    user_id = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    project_id = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )

    granted_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["UserModel"] = relationship(
        back_populates="project_accesses",
    )

    project: Mapped["ProjectModel"] = relationship(
        back_populates="project_accesses",
    )