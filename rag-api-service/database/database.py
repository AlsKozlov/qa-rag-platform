from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_async_engine(settings.DATABASE_URL)
session_maker = sessionmaker(engine, class_ = AsyncSession, expire_on_commit = False)

async def get_session():
    async with session_maker() as session:
        yield session

class BaseDB(DeclarativeBase):
    pass
