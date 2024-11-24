from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = "postgresql+asyncpg://username:password@localhost/dbname"




settings = Settings()

engine = create_async_engine(settings.database_url, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session():
    async with async_session() as session:
        yield session
