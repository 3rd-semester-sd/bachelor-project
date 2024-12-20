from typing import Annotated
from fastapi import Depends, Request
from redis.asyncio import Redis


def get_redis(request: Request) -> Redis:  # type: ignore
    """Get redis connection."""

    return request.app.state.redis


GetRedis = Annotated[Redis, Depends(get_redis)]
