from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from settings import settings
import sqlalchemy as sa


async def setup_db(app: FastAPI) -> None:  # pragma: no cover
    """Setup database."""
    engine = create_async_engine(
        str(settings.DB_URL),
        echo=True,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    app.state.db_engine = engine
    app.state.db_session = session_factory

    async with engine.begin() as connection:
        await connection.run_sync(sa.MetaData().create_all)

    await engine.dispose()
