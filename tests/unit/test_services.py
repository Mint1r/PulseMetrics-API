
from src.api.security.auth import is_authenticated, delete_session
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

@pytest.mark.asyncio
async def test_is_authenticated():
    mock_redis = AsyncMock()
    mock_db_session = AsyncMock()

    get_session_user_id_mock = AsyncMock(return_value=42)

    with patch(
            "src.api.security.auth.get_session_user_id",
            get_session_user_id_mock
        ):
            user_id = await is_authenticated(
                session_id="some_session_token",
                session_db=mock_db_session,
                redis=mock_redis,
            )

    assert user_id == 42

    get_session_user_id_mock.assert_awaited_once()
    mock_db_session.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_is_authenticated_user_id_None():
    mock_redis = AsyncMock()
    mock_db_session = AsyncMock()
    result_mock = MagicMock()
    mock_db_session.execute.return_value = result_mock
    result_mock.one_or_none.return_value = None

    get_session_user_id_mock = AsyncMock(return_value=None)
    cache_session_mock = AsyncMock()

    with (patch(
            "src.api.security.auth.get_session_user_id",
            get_session_user_id_mock
        ),
        patch(
            "src.api.security.auth.cache_session",
            cache_session_mock,
        ),
    ):
            user_id = await is_authenticated(
                session_id="some_session_token",
                session_db=mock_db_session,
                redis=mock_redis,
            )

    assert user_id == None

    get_session_user_id_mock.assert_awaited_once()
    mock_db_session.execute.assert_awaited_once()
    cache_session_mock.assert_not_awaited()

@pytest.mark.asyncio
async def test_is_authenticated_user_id_get_from_db():
    mock_redis = AsyncMock()
    mock_db_session = AsyncMock()
    result_mock = MagicMock()
    session_mock = MagicMock()
    mock_db_session.execute.return_value = result_mock
    result_mock.one_or_none.return_value = session_mock
    session_mock.user_id = 42

    get_session_user_id_mock = AsyncMock(return_value=None)
    cache_session_mock = AsyncMock()

    with (patch(
            "src.api.security.auth.get_session_user_id",
            get_session_user_id_mock
        ),
        patch(
            "src.api.security.auth.cache_session",
            cache_session_mock,
        ),
    ):
            user_id = await is_authenticated(
                session_id="some_session_token",
                session_db=mock_db_session,
                redis=mock_redis,
            )

    assert user_id == 42

    get_session_user_id_mock.assert_awaited_once()
    mock_db_session.execute.assert_awaited_once()
    cache_session_mock.assert_awaited_once()

@pytest.mark.asyncio
async def test_is_authenticated_session_id_None():
    mock_redis = AsyncMock()
    mock_db_session = AsyncMock()

    get_session_user_id_mock = AsyncMock(return_value=42)

    with patch(
            "src.api.security.auth.get_session_user_id",
            get_session_user_id_mock
        ):
            user_id = await is_authenticated(
                session_id=None,
                session_db=mock_db_session,
                redis=mock_redis,
            )

    assert user_id == None

    get_session_user_id_mock.assert_not_awaited()
    mock_db_session.assert_not_awaited()

@pytest.mark.asyncio
async def test_delete_session():
    mock_redis = AsyncMock()
    mock_db_session = AsyncMock()
    result_mock = MagicMock()
    session_mock = MagicMock()
    mock_db_session.execute.return_value = result_mock
    result_mock.scalar_one_or_none.return_value = session_mock

    user_id = await delete_session(
        session_id="some_session_token",
        session_db=mock_db_session,
        redis=mock_redis,
    )

    assert user_id == None

    mock_db_session.execute.assert_awaited_once()
    mock_db_session.delete.assert_awaited_once()
    mock_db_session.commit.assert_awaited_once()
    mock_redis.delete.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_session_None():
    mock_redis = AsyncMock()
    mock_db_session = AsyncMock()
    result_mock = MagicMock()
    mock_db_session.execute.return_value = result_mock
    result_mock.scalar_one_or_none.return_value = None

    user_id = await delete_session(
        session_id="some_session_token",
        session_db=mock_db_session,
        redis=mock_redis,
    )

    assert user_id == None

    mock_db_session.execute.assert_awaited_once()
    mock_db_session.delete.assert_not_awaited()
    mock_db_session.commit.assert_not_awaited()
    mock_redis.delete.assert_awaited_once()
