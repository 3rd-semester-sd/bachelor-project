from settings import PGSettings, settings

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


async def _setup(
    app: FastAPI,
    pg_settings: PGSettings,
    suffix: str = "",
) -> None:
    """Setup database."""

    engine = create_async_engine(
        str(pg_settings.url),
        echo=pg_settings.echo,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    setattr(app.state, f"db_engine{suffix}", engine)
    setattr(app.state, f"db_session{suffix}_factory", session_factory)

    await engine.dispose()


async def setup_db_ro(app: FastAPI) -> None:
    """Setup read only database."""

    await _setup(app, settings.pg_ro, "_ro")


async def setup_db(app: FastAPI) -> None:
    """Setup database."""

    await _setup(app, settings.pg)


async def shutdown_db(app: FastAPI) -> None:
    """Shutdown database."""

    await app.state.db_engine.dispose()


async def shutdown_db_ro(app: FastAPI) -> None:
    """Shutdown read only database."""

    await app.state.db_engine_ro.dispose()
