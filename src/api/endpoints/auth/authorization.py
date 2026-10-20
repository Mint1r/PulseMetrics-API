from fastapi import APIRouter, Depends, status,Response
from redis.asyncio import Redis
from src.domain.schemas.user import UserAuthSchema
from src.domain.models.session import SessionModel
from src.domain.models.user import UserModel
from src.domain.schemas.user import UserResponseSchema
from src.core.redis_client import get_redis
from src.core.postgres import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.security.password import hash_password, verify_password
from src.api.security.session import hash_session,generate_session
from fastapi import APIRouter, Depends, Response, HTTPException, status, Cookie
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.handlers import cache_session
from redis.exceptions import RedisError
from src.api.security.auth import delete_session
from fastapi.responses import RedirectResponse
from src.api.security.auth import SESSION_CACHE_TTL
from sqlalchemy.exc import IntegrityError

auth_router = APIRouter(prefix = "/users")

@auth_router.post(
    '/login',
    response_model = UserResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Вход в аккаунт",
    description="Проверяет учётные данные пользователя и создаёт новую сессию.")

async def login(
    user_data: UserAuthSchema,
    response: Response,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    ) -> UserResponseSchema:

    result = await session.execute(
        select(UserModel).where(
            UserModel.email == user_data.email
        )
    )

    user_obj = result.scalar_one_or_none()

    if user_obj is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    
    if not verify_password(
        user_data.password.get_secret_value(),
        user_obj.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    session_token = generate_session()
    token_hash = hash_session(session_token)

    session_obj = SessionModel(
        token_hash=token_hash,
        user=user_obj,
    )

    session.add(session_obj)

    await session.commit()


    try:
        await cache_session(
            redis = redis,
            token_hash = token_hash,
            user_id = user_obj.id,
            ttl = SESSION_CACHE_TTL
            )
    except RedisError:
        pass


    response.set_cookie(
        key="session_id",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,
    )

    return UserResponseSchema(
        id=user_obj.id,
        email=user_obj.email,
        created_at = user_obj.created_at
    )


@auth_router.post(
    '/registration',
    response_model = UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Зарегестрировать пользователя",
    description="Создаёт новый project")
async def registration(
    project_data: UserAuthSchema,
    response: Response,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    ) -> UserResponseSchema:
    
    session_token = generate_session()
    token_hash = hash_session(session_token)
    password_hash = hash_password(project_data.password.get_secret_value())


    try:
        async with session.begin():
            user_obj = UserModel(
                email = project_data.email, 
                password_hash = password_hash)
            session.add(user_obj)


            session_obj = SessionModel(
                token_hash = token_hash, 
                user = user_obj,
                )
            session.add(session_obj)
            
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        ) from exc

    response.set_cookie(
        key="session_id",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,
    )
    
    try:
        await cache_session(
            redis = redis,
            token_hash = token_hash,
            user_id = user_obj.id,
            ttl = SESSION_CACHE_TTL
            )
    except RedisError:
        pass

    return UserResponseSchema(
        id=user_obj.id,
        email=user_obj.email,
        created_at = user_obj.created_at
    )

@auth_router.post("/logout")
async def logout(
    session_id: str | None = Cookie(default=None),
    session_db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    if session_id:
        await delete_session(
            session_id = session_id,
            session_db = session_db,
            redis = redis)

    redirect = RedirectResponse(
        "/users/login",
        status_code=303,
    )

    redirect.delete_cookie(
        key="session_id",
        path="/",
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return redirect

