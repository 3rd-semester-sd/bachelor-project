from settings import settings

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from db import meta
import sqlalchemy as sa

from loguru import logger


async def setup_db_ro(app: FastAPI) -> None:
    """Setup read only database."""

    engine = create_async_engine(
        str(settings.pg_ro.url),
        echo=settings.pg_ro.echo,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    app.state.db_engine_ro = engine
    app.state.db_session_ro_factory = session_factory

    await engine.dispose()


async def setup_db(app: FastAPI) -> None:
    """Setup database."""

    engine = create_async_engine(
        str(settings.pg.url),
        echo=settings.pg.echo,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    app.state.db_engine = engine
    app.state.db_session_factory = session_factory

    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)
        if settings.pg_ro.url != settings.pg.url and settings.environment == "local":
            logger.info("Setting up read only user permissions.")
            query = f"""
            GRANT SELECT ON ALL TABLES IN SCHEMA public TO {settings.pg_ro.user};
            """

            await conn.execute(sa.text(query))

            query = f"""
            ALTER DEFAULT PRIVILEGES IN SCHEMA public
            GRANT SELECT ON TABLES TO {settings.pg_ro.user};
            """

            await conn.execute(sa.text(query))

    await engine.dispose()


async def shutdown_db(app: FastAPI) -> None:
    """Shutdown database."""

    await app.state.db_engine.dispose()


async def shutdown_db_ro(app: FastAPI) -> None:
    """Shutdown read only database."""

    await app.state.db_engine_ro.dispose()
