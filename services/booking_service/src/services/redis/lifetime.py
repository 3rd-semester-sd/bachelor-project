from redis.asyncio import Redis
from fastapi import FastAPI
from settings import settings


def setup_redis(app: FastAPI) -> None:
    """Setup Redis."""
    app.state.redis = Redis.from_url(
        str(settings.redis.url),
        auto_close_connection_pool=False,
    )


async def shutdown_redis(app: FastAPI) -> None:
    """Shutdown Redis."""
    redis: Redis = app.state.redis
    await redis.close()
