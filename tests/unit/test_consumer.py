
from src.consumers.consumer import process_events, process_panding_events
from unittest.mock import AsyncMock, MagicMock, patch
import pytest



@pytest.mark.asyncio
async def test_process_events():

    events = [
        (
            "1744631234567-0",
            {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "data": '{"project_id": "9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c", "event_type": "cart_item_added", "session_id": "sess_abc123xyz", "properties": {}, "timestamp": "2026-08-14T15:00:00Z"}'
            }
        )
    ]

    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session_local = MagicMock()

    mock_session_local.return_value.__aenter__.return_value = mock_session

    redis = AsyncMock()
    

    with patch(
        "src.consumers.consumer.AsyncSessionLocal",
        mock_session_local
    ):
        await process_events(events, redis)

    mock_session.execute.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_not_awaited()

    redis.xack.assert_awaited_once()
    redis.xdel.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_events_xack_failed():

    events = [
        (
            "1744631234567-0",
            {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "data": '{"project_id": "9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c", "event_type": "cart_item_added", "session_id": "sess_abc123xyz", "properties": {}, "timestamp": "2026-08-14T15:00:00Z"}'
            }
        )
    ]

    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session_local = MagicMock()

    mock_session_local.return_value.__aenter__.return_value = mock_session

    redis = AsyncMock()
    redis.xack.side_effect = Exception("Redis XACK failed")

    with pytest.raises(Exception, match="Redis XACK failed"):
        with patch(
            "src.consumers.consumer.AsyncSessionLocal",
            mock_session_local
        ):
            await process_events(events, redis)

    redis.xack.assert_awaited_once()
    redis.xdel.assert_not_awaited()

@pytest.mark.asyncio
async def test_process_events_xdel_failed():

    events = [
        (
            "1744631234567-0",
            {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "data": '{"project_id": "9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c", "event_type": "cart_item_added", "session_id": "sess_abc123xyz", "properties": {}, "timestamp": "2026-08-14T15:00:00Z"}'
            }
        )
    ]

    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session_local = MagicMock()

    mock_session_local.return_value.__aenter__.return_value = mock_session

    redis = AsyncMock()
    redis.xdel.side_effect = Exception("Redis XDEL failed")

    with pytest.raises(Exception, match="Redis XDEL failed"):
        with patch(
            "src.consumers.consumer.AsyncSessionLocal",
            mock_session_local
        ):
            await process_events(events, redis)

    redis.xack.assert_awaited_once()
    redis.xdel.assert_awaited_once()

@pytest.mark.asyncio
async def test_process_events_commit_failed():

    events = [
        (
            "1744631234567-0",
            {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "data": '{"project_id": "9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c", "event_type": "cart_item_added", "session_id": "sess_abc123xyz", "properties": {}, "timestamp": "2026-08-14T15:00:00Z"}'
            }
        )
    ]

    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session_local = MagicMock()

    mock_session_local.return_value.__aenter__.return_value = mock_session

    redis = AsyncMock()

    mock_session.commit.side_effect = Exception("Database commit failed")
    
    with pytest.raises(Exception, match="Database commit failed"):
        with patch(
            "src.consumers.consumer.AsyncSessionLocal",
            mock_session_local
        ):
            await process_events(events, redis)

    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()
    redis.xack.assert_not_awaited()
    redis.xdel.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_panding_events():

    events = [
        (
            "1744631234567-0",
            {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "data": '{"project_id": "9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c", "event_type": "cart_item_added", "session_id": "sess_abc123xyz", "properties": {}, "timestamp": "2026-08-14T15:00:00Z"}'
            }
        )
    ]

    mock_process_events = AsyncMock()
    redis = AsyncMock()
    redis.hincrby.return_value = 1

    with patch(
            "src.consumers.consumer.process_events",
            mock_process_events
        ):
        await process_panding_events(events, redis)
    redis.hincrby.assert_awaited_once()
    redis.xack.assert_not_awaited()
    redis.xdel.assert_not_awaited()
    redis.hdel.assert_not_awaited()
    mock_process_events.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_panding_events_retry_limit_exceeded():

    events = [
        (
            "1744631234567-0",
            {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "data": '{"project_id": "9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c", "event_type": "cart_item_added", "session_id": "sess_abc123xyz", "properties": {}, "timestamp": "2026-08-14T15:00:00Z"}'
            }
        )
    ]

    mock_process_events = AsyncMock()
    redis = AsyncMock()
    redis.hincrby.return_value = 6


    with patch(
            "src.consumers.consumer.process_events",
            mock_process_events
        ):
        await process_panding_events(events, redis)

    redis.hincrby.assert_awaited_once()
    redis.xack.assert_awaited_once()
    redis.xdel.assert_awaited_once()
    redis.hdel.assert_awaited_once()
    redis.xadd.assert_awaited_once()

    mock_process_events.assert_not_awaited()



        
