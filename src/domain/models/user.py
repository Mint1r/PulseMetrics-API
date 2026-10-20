from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from src.core.postgres import Base
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    sessions: Mapped[list["SessionModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    project_accesses: Mapped[list["ProjectAccessModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )