import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection
from aio_pika.pool import Pool
from notification_handler import NotificationHandler, NotificationRequestDTO
from settings import RabbitMQSettings
import json
from loguru import logger

from typing import Any


async def _init_consumer(
    state: dict[str, Any],
) -> None:
    """Initialize consumer for rabbitmq."""

    channel_pool: Pool[aio_pika.Channel] = state["rmq_channel_pool"]

    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(
            name="bachelor_exchange",
            auto_delete=True,
            type="direct",
        )
        queue = await channel.declare_queue("notification", durable=False)
        await queue.bind(exchange, routing_key="send_notification_queue")

        async def _message_handler(
            message: aio_pika.abc.AbstractIncomingMessage,
        ) -> None:
            async with message.process():
                msg = message.body.decode()
                data = json.loads(msg)

                if "notification_type" not in data:
                    logger.error("notification_type not in message")
                    return

                notification_type = data["notification_type"]

                handler_cls = NotificationHandler.get_handler(notification_type)

                if handler_cls is None:
                    logger.error(
                        f"Handler not found for notification type {notification_type}"
                    )
                    return

                handler = handler_cls()

                await handler.handle(
                    data=NotificationRequestDTO(**data),
                )

        await queue.consume(_message_handler)


async def init_rabbit(
    state: dict[str, Any],
    settings: RabbitMQSettings,
) -> None:
    """Initialize rabbitmq pools."""

    async def _get_connection() -> AbstractRobustConnection:
        return await aio_pika.connect_robust(str(settings.url))

    connection_pool: Pool[AbstractRobustConnection] = Pool(
        _get_connection, max_size=settings.rabbit_pool_size
    )

    async def _get_channel() -> AbstractChannel:
        async with connection_pool.acquire() as conn:
            return await conn.channel()

    channel_pool: Pool[aio_pika.Channel] = Pool(
        _get_channel, max_size=settings.rabbit_channel_pool_size
    )

    state["rmq_pool"] = connection_pool
    state["rmq_channel_pool"] = channel_pool

    await _init_consumer(state)


async def shutdown_rabbit(
    state: dict[str, Any],
) -> None:
    """Close all connection and pools."""

    rmq_channel_pool: Pool[aio_pika.Channel] = state["rmq_channel_pool"]
    rmq_pool: Pool[AbstractRobustConnection] = state["rmq_pool"]

    await rmq_channel_pool.close()
    await rmq_pool.close()
