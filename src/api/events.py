
from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from src.domain.schemas.event import EventCreateSchema, EventResponseSchema
from src.core.redis_client import get_redis

router = APIRouter(prefix = "/api/v1/events", tags=["Events Ingestion"])

@router.post(
    '',
    response_model = EventResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Принять событие аналитики",
    description="Валидирует входящий JSON и мгновенно отправляет событие в Redis Stream.")

async def ingest_event(
    event: EventCreateSchema,
    redis: Redis = Depends(get_redis)) -> EventResponseSchema:

    response = EventResponseSchema()

    payload = {
        'event_id': str(response.event_id),
        'data': event.model_dump_json(exclude={"api_key"})
    }

    await redis.xadd(name="events_stream", fields=payload)
    return response
