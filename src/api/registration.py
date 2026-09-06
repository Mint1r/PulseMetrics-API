
from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from src.domain.schemas.registration import ProjectCreateSchema, RegistrationResponseSchema
from src.domain.models.project import ProjectModel
from src.core.redis_client import get_redis
from src.core.postgres import get_db
import secrets, uuid, hashlib
from sqlalchemy.ext.asyncio import AsyncSession

register_router = APIRouter(prefix = "/api/v1/registration", tags=["Registration Ingestion"])

def generate_api_key() -> str:
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()

@register_router.post(
    '',
    response_model = RegistrationResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Зарегестрировать пользователя",
    description="Создаёт новый project")

async def ingest_event(
    project_data: ProjectCreateSchema,
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_db)) -> RegistrationResponseSchema:

    api_key = generate_api_key()
    hashed_api_key = hash_api_key(api_key)
    project_id = uuid.uuid4()
    response = RegistrationResponseSchema(api_key=api_key,project_id=project_id)

    project_obj = ProjectModel(id = project_id, api_key = hashed_api_key, title = project_data.title)
    session.add(project_obj)
    await session.commit()

    await redis.hset("projects-data", str(project_id), hashed_api_key)
    return response
