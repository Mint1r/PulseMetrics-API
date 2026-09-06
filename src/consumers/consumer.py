
from sqlalchemy.dialects.postgresql import insert
import asyncio
from redis.asyncio import Redis
from src.core.postgres import AsyncSessionLocal
from src.domain.models.event import EventModel
import json
from uuid import UUID
from datetime import datetime
from src.core.config import REDIS_URL

STREAM_NAME = "events_stream"
GROUP_NAME = "analytics"
CONSUMER_NAME = "worker-1"
DLQ_STREAM_NAME = 'dlq_stream'
BATCH_SIZE = 2000
BLOCK_MS = 5000
MAX_RETRIES = 5


async def process_panding_events(events,redis):
    events_to_process = []  
    for redis_id, data in events:
        retry_count = await redis.hincrby(
            'event_retries',
            redis_id,
            1
        )
        if retry_count <= MAX_RETRIES:
            events_to_process.append((redis_id,data))

        else: 
            try:
                await redis.xadd(
                    name = DLQ_STREAM_NAME,
                    fields = {
                        "event_id": data["event_id"],
                        'redis_id': redis_id,
                        'data' : json.dumps(data)
                    }
                )

            except Exception as e:
                print(f"Ошибка XADD: {e}")
                raise

            try:
                await redis.xack(
                    STREAM_NAME,
                    GROUP_NAME,
                    redis_id,
                )

            except Exception as e:
                print(f"Ошибка XACK: {e}")
                raise


            try:
                await redis.xdel(
                    STREAM_NAME,
                    redis_id,
                )

            except Exception as e:
                print(f"Ошибка XDEL: {e}")
                raise

            try:
                await redis.hdel(
                    'event_retries',
                    redis_id,
                )

            except Exception as e:
                print(f"Ошибка HDEL: {e}")
                raise



    if events_to_process:
        try:
            await process_events(events=events_to_process,redis=redis)
        except Exception as e:
            print(f"Ошибка process_panding_events: {e}")
            raise
    else: return
            


async def process_events(events,redis):
    async with AsyncSessionLocal() as session:      
        db_objects = []

        redis_ids = []

        for redis_id, data in events:
            event_data = json.loads(data["data"])
            event_data["timestamp"] = datetime.fromisoformat(
                event_data["timestamp"].replace("Z", "+00:00")
            )

            redis_ids.append(redis_id)

            db_objects.append(
                {
                    'id':UUID(data["event_id"]),
                    **event_data,
                }
            )

        if db_objects == []:
            return


        try:
            stmt = insert(EventModel).values(db_objects)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[EventModel.id]
            )
            await session.execute(stmt)
            await session.commit()

        except Exception as e:
            await session.rollback()
            print(f"Ошибка БД: {e}")
            raise


        try:
            await redis.xack(
                STREAM_NAME,
                GROUP_NAME,
                *redis_ids,
            )

        except Exception as e:
            print(f"Ошибка XACK: {e}")
            raise

        try:
            await redis.xdel(
                STREAM_NAME,
                *redis_ids,
            )

        except Exception as e:
            print(f"Ошибка XDEL: {e}")
            raise

        try:
            await redis.hdel(
                'event_retries',
                *redis_ids,
            )

        except Exception as e:
            print(f"Ошибка HDEL: {e}")
            raise

    




async def consume():
    redis = Redis.from_url(REDIS_URL,socket_timeout=None,decode_responses=True,)
    start_id = '0-0'

    try: 

    # Создаём Consumer Group один раз
        try:
            await redis.xgroup_create(
                name=STREAM_NAME,
                groupname=GROUP_NAME,
                id="0",
                mkstream=True,
            )
        except Exception as e:
            # Группа уже существует
            if "BUSYGROUP" not in str(e):
                raise

        while True:
            messages = await redis.xreadgroup(
                groupname=GROUP_NAME,
                consumername=CONSUMER_NAME,
                streams={
                    STREAM_NAME: ">"
                },
                count=BATCH_SIZE,
                block=BLOCK_MS,
            )

            if messages:

                events = messages[0][1]

                try: 
                    await process_events(events=events,redis=redis)
                except Exception as e:
                    print(f"Ошибка обработки batch: {e}")
                    await asyncio.sleep(1)

            pending_messages = await redis.xautoclaim(
                name=STREAM_NAME,
                groupname=GROUP_NAME,
                consumername=CONSUMER_NAME,
                min_idle_time=30000,
                start_id=start_id,
                count=BATCH_SIZE,
            )
            start_id = pending_messages[0]

            pending_events = pending_messages[1]

            if pending_events:
                try:
                    await process_panding_events(
                        events=pending_events,
                        redis=redis
                    )
                except Exception as e:
                    print(f"Ошибка обработки pending_events: {e}")
                    await asyncio.sleep(1)            
    finally:
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(consume())