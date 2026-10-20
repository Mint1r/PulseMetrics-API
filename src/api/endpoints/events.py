
from fastapi import APIRouter, Depends, status,Security
from redis.asyncio import Redis
from src.domain.schemas.event import EventCreateSchema, EventResponseSchema
from src.core.redis_client import get_redis
from src.api.security.password import api_key_header, validate_project_access

api_router = APIRouter(prefix = "/api/v1")

@api_router.post(
    '/events',
    response_model = EventResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Принять событие аналитики",
    description="Валидирует входящий JSON и мгновенно отправляет событие в Redis Stream.")
async def ingest_event(
    event: EventCreateSchema,
    redis: Redis = Depends(get_redis),
    api_key: str = Security(api_key_header),
    ) -> EventResponseSchema:

    await validate_project_access(
        project_id=event.project_id, 
        api_key=api_key,
        redis=redis
        )

    response = EventResponseSchema()

    payload = {
        'event_id': str(response.event_id),
        'data': event.model_dump_json()
    }

    await redis.xadd(name="events_stream", fields=payload)
    return response
