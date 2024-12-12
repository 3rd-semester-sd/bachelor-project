from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.db.meta import meta
from app.settings import settings


async def setup_db(app: FastAPI) -> None:  # pragma: no cover
    """Setup database."""
    engine = create_async_engine(
        str(settings.ai_database_url),
        echo=True,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    app.state.db_engine = engine
    app.state.db_session = session_factory

    async with engine.begin() as connection:
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await connection.run_sync(meta.create_all)

    await engine.dispose()
