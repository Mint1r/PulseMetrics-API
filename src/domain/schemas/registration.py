from uuid import UUID
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class RegistrationResponseSchema(BaseModel):
    status: str = Field(
        default="queued",
        examples=["queued"],
    )

    project_id: UUID = Field(
        description="Уникальный идентификатор проекта",
    )

    api_key: str = Field(
        default_factory=uuid4,
        description="Секретный API-ключ проекта",
    )

class ProjectCreateSchema(BaseModel):
    title : str = Field(description="Название проекта")