
from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from src.domain.schemas.event import EventCreateSchema, EventResponseSchema
from src.core.redis_client import get_redis
from fastapi import HTTPException
import hashlib
router = APIRouter(prefix = "/api/v1/events", tags=["Events Ingestion"])

def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()

async def data_check(id:str,api_key:str,redis):
    real_key = await redis.hget('projects-data',id)
    if not real_key:
        return False
    if real_key != hash_api_key(api_key):
        return False
    return True
    

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

    if not await data_check(str(event.project_id), event.api_key,redis=redis):
        raise HTTPException(
            status_code=401,
            detail="Invalid project credentials"
        )

    await redis.xadd(name="events_stream", fields=payload)
    return response
