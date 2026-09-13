from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import Generator
from sqlalchemy.orm import Session
from . config import DATABASE_URL_TEST_SYNC as DATABASE_URL


engine = create_engine(
    DATABASE_URL,
)

TestSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()