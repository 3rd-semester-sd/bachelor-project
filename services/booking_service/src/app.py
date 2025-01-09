from services.rabbit.lifetime import (
    init_rabbit,
    shutdown_rabbit,
)
from settings import settings

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from routes import base_router
from db import db_lifetime
from loguru import logger
from services.redis import lifetime as redis_lifetime
from services.http_client import lifetime as http_client_lifetime


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan."""

    logger.info(settings.pg.url)
    logger.info(settings.pg_ro.url)
    await db_lifetime.setup_db_ro(app)
    await db_lifetime.setup_db(app)
    await http_client_lifetime.init_http_client(app)
    redis_lifetime.setup_redis(app)
    init_rabbit(app)

    yield

    await db_lifetime.shutdown_db_ro(app)
    await db_lifetime.shutdown_db(app)
    await http_client_lifetime.shutdown_http_client(app)
    await redis_lifetime.shutdown_redis(app)
    await shutdown_rabbit(app)


def get_app() -> FastAPI:
    """Get FastAPI app."""
    logger.info(
        settings.model_dump_json(indent=2),
    )

    app = FastAPI(lifespan=lifespan, root_path="/booking-service")
    app.include_router(base_router)
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:get_app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=settings.reload,
        lifespan="on",
        factory=True,
    )
