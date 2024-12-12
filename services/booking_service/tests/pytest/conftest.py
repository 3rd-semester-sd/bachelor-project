import pytest
from src.db.db_dependencies import get_db_session
from services.booking_service.src.app import get_app
from fastapi import FastAPI
from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from typing import AsyncGenerator, AsyncIterator

import pytest

from sqlalchemy.ext.asyncio import AsyncEngine

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    AsyncTransaction,
    async_sessionmaker,
    create_async_engine,
)
from src.daos import DAOs
from src.settings import settings
from src.db.db_utils import create_database, drop_database


@pytest.fixture(scope="session")
def session_app() -> FastAPI:
    """Get FastAPI app (session wide, db will be invalid)."""
    return get_app()


@pytest.fixture
def overwritten_deps(
    dbsession: AsyncSession,
) -> dict[Any, Any]:
    """Get dependencies that will be overwritten."""

    return {
        get_db_session: lambda: dbsession,
    }


@pytest.fixture
def app(
    session_app: FastAPI,
    overwritten_deps: dict[Any, Any],
) -> FastAPI:
    """Fixture for creating FastAPI app with mocked dependencies."""

    app = session_app
    app.dependency_overrides.update(overwritten_deps)

    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=app, base_url="http://test" + "/booking-service") as ac:
        yield ac


@pytest.fixture
async def _engine() -> AsyncIterator[AsyncEngine]:
    """Create engine and databases."""
    from src.db import meta

    await create_database("test_db")

    engine = create_async_engine(str(settings.pg.url) + "/test_db")
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database("test_db")


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Session with a SAVEPOINT, that it will rollback to after the test completes.
    """
    connection = await _engine.connect()
    tx = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session  # type: ignore
    finally:
        await session.close()
        await try_rollback(tx)
        await connection.close()


async def try_rollback(rollbackable: AsyncSession | AsyncTransaction) -> None:
    """Try to rollback session."""
    try:
        await rollbackable.rollback()
    except Exception:
        return


@pytest.fixture(autouse=True)
def inject_session_to_factories(
    dbsession: AsyncSession,
) -> None:
    """Inject session to factories."""
    # factory.AsyncFactory.session = dbsession


@pytest.fixture
def daos(dbsession: AsyncSession) -> DAOs:
    """Return DAOs for all tables in database."""
    return DAOs(dbsession)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Anyio backend."""
    return "asyncio"
