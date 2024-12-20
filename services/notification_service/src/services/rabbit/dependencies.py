from typing import Annotated

from aio_pika import Channel
from aio_pika.pool import Pool
from fastapi import Depends, Request


def get_rmq_channel_pool(request: Request) -> Pool[Channel]:  # pragma: no cover
    """
    Get channel pool from the state.

    :param request: current request.
    :return: channel pool.
    """
    return request.app.state.rmq_channel_pool


class RMQService:
    """RabbitMQ Service."""

    def __init__(self, pool: Pool[Channel] = Depends(get_rmq_channel_pool)) -> None:
        self.pool = pool

    async def _consume(self, queue_name: str, callback) -> None:
        """
        Consume messages from the queue.

        :param queue_name: name of the queue.
        :param callback: callback function.
        """
        async with self.pool.acquire() as channel:
            queue = await channel.declare_queue(queue_name, durable=True)
            await queue.consume(callback)


GetRMQ = Annotated[RMQService, Depends(RMQService)]
