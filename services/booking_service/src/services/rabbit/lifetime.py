import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection
from aio_pika.pool import Pool
from fastapi import FastAPI
from settings import settings


def init_rabbit(app: FastAPI) -> None:  # pragma: no cover
    """Initialize rabbitmq pools."""

    async def get_connection() -> AbstractRobustConnection:
        """Creates connection to RabbitMQ using url from settings."""
        return await aio_pika.connect_robust(str(settings.rabbit.url))

    connection_pool: Pool[AbstractRobustConnection] = Pool(
        get_connection,
        max_size=settings.rabbit.rabbit_pool_size,
    )

    async def get_channel() -> AbstractChannel:
        """Open channel on connection."""
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    channel_pool: Pool[aio_pika.Channel] = Pool(
        get_channel,
        max_size=settings.rabbit.rabbit_channel_pool_size,
    )

    app.state.rmq_pool = connection_pool
    app.state.rmq_channel_pool = channel_pool


async def shutdown_rabbit(app: FastAPI) -> None:  # pragma: no cover
    """Close all connection and pools."""
    await app.state.rmq_channel_pool.close()
    await app.state.rmq_pool.close()
