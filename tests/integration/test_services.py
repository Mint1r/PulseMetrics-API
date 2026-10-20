
from src.api.security.auth import is_authenticated, delete_session
import pytest
import uuid
from src.api.security.session import hash_session
from src.api.handlers  import cache_session,get_session_user_id
from src.domain.models.session import SessionModel
from src.domain.models.user import UserModel
from sqlalchemy import select

@pytest.mark.asyncio
async def test_is_authenticated_from_db(test_redis,db_session):

    id = uuid.uuid4()
    user = UserModel(
            id=id,
            email = 'test@test',
            password_hash = '',
    )

    session = SessionModel(
        user_id = id,
        token_hash = hash_session('kjnbkajbviklawghrlwbeflIOWEFHOWUEfhgWKHEBFKHo'),
    )

    db_session.add_all([user, session])
    await db_session.commit()

    user_id = await is_authenticated(
        session_id="kjnbkajbviklawghrlwbeflIOWEFHOWUEfhgWKHEBFKHo",
        session_db=db_session,
        redis=test_redis,
    )

    assert user_id == id

@pytest.mark.asyncio
async def test_is_authenticated_from_redis(test_redis,db_session):

    id = uuid.uuid4()
    user = UserModel(
            id=id,
            email = 'test@test',
            password_hash = '',
    )

    session = SessionModel(
        user_id = id,
        token_hash = hash_session('kjnbkajbviklawghrlwbeflIOWEFHOWUEfhgWKHEBFKHo'),
    )

    db_session.add_all([user, session])
    await db_session.commit()

    await cache_session(
        redis=test_redis,
        token_hash=hash_session('kjnbkajbviklawghrlwbeflIOWEFHOWUEfhgWKHEBFKHo'),
        user_id=id,
        ttl=600
    )

    user_id = await is_authenticated(
        session_id="kjnbkajbviklawghrlwbeflIOWEFHOWUEfhgWKHEBFKHo",
        session_db=db_session,
        redis=test_redis,
    )

    assert user_id == str(id)

@pytest.mark.asyncio
async def test_is_authenticated_no_session(test_redis,db_session):

    user_id = await is_authenticated(
        session_id="kjnbkajbviklawghrlwbeflIOWEFHOWUEfhgWKHEBFKHo",
        session_db=db_session,
        redis=test_redis,
    )

    assert user_id == None


@pytest.mark.asyncio
async def test_is_authenticated_no_session_id(test_redis,db_session):

    user_id = await is_authenticated(
        session_id=None,
        session_db=db_session,
        redis=test_redis,
    )

    assert user_id == None


@pytest.mark.asyncio
async def test_delete_session(test_redis,db_session):

    id = uuid.uuid4()
    user = UserModel(
            id=id,
            email = 'test@test',
            password_hash = '',
    )
    token_hash = hash_session('kjnbkajbviklawghrlwbeflIOWEFHOWUEfhgWKHEBFKHo')

    session = SessionModel(
        user_id = id,
        token_hash = token_hash,
    )
    

    db_session.add_all([user, session])
    await db_session.commit()

    await cache_session(
        redis=test_redis,
        token_hash=token_hash,
        user_id=id,
        ttl=600
    )

    result1 = await delete_session(
        session_id="kjnbkajbviklawghrlwbeflIOWEFHOWUEfhgWKHEBFKHo",
        session_db=db_session,
        redis=test_redis,
    )

    assert result1 == None

    user_id = await get_session_user_id(
        redis=test_redis,
        token_hash = token_hash)

    assert user_id == None

    result2 = await db_session.execute(
        select(SessionModel).where(
            SessionModel.token_hash == token_hash
        )
    )

    assert result2.scalar_one_or_none() is None
    
@pytest.mark.asyncio
async def test_delete_session_no_session(test_redis, db_session):
    session_id = "kjnbkajbviklawghrlwbeflIOWEFHOWUEfhgWKHEBFKHo"
    token_hash = hash_session(session_id)

    await cache_session(
        redis=test_redis,
        token_hash=token_hash,
        user_id=uuid.uuid4(),
        ttl=600,
    )

    result = await delete_session(
        session_id=session_id,
        session_db=db_session,
        redis=test_redis,
    )

    assert result is None

    cached_user_id = await get_session_user_id(
        redis=test_redis,
        token_hash=token_hash,
    )
    assert cached_user_id is None