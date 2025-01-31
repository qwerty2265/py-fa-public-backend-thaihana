from datetime import datetime

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, TIMESTAMP

from config import DB_HOST, DB_NAME, DB_PASS, DB_USER

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"


class Base(DeclarativeBase):
    id = Column(Integer, primary_key=True)

    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    modified_at = Column(TIMESTAMP, default=datetime.utcnow())


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

