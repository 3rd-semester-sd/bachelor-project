import json
from typing import Annotated
from uuid import UUID
from aio_pika import IncomingMessage
from aio_pika import Channel
from aio_pika.pool import Pool
from fastapi import Depends, Request, logger
from openai import AsyncAzureOpenAI
from pydantic import BaseModel

from app.db.dependencies import ElasticsearchService
from app.services.embeddings import generate_restaurant_embedding
from app.api.dtos.chat_dtos import RestaurantInputDTO


def get_rmq_channel_pool(request: Request) -> Pool[Channel]:  # pragma: no cover
    """
    Get channel pool from the state.

    :param request: current request.
    :return: channel pool.
    """
    return request.app.state.rmq_channel_pool


class RMQService:
    """RabbitMQ Service."""

    def __init__(
        self,
        pool: Pool[Channel],
        ai_client: AsyncAzureOpenAI,
        es_service: ElasticsearchService,
    ) -> None:
        self.pool = pool
        self.ai_client = ai_client
        self.es_service = es_service

    async def handle_message(self, message: IncomingMessage) -> None:
        print("hello")
        async with message.process():
            print("hello, INSIDE")
            try:
                body_str = message.body.decode("utf-8")
                data = RestaurantInputDTO.model_validate_json(body_str)

                print(f"Received message: {data}")

                # generate embedding based on input
                await generate_restaurant_embedding(
                    data, self.ai_client, self.es_service
                )
            except Exception as e:
                logger.logger.error(f"Error processing message: {e}")

    async def declare_and_consume(self):
        """
        Declare the queue, and start consuming it.
        When a message is received notify the user.
        """

        async with self.pool.acquire() as conn:
            queue_name = "new_restaurant_queue"
            print("declaring", queue_name)
            queue = await conn.declare_queue(queue_name, durable=True)
        # start consuming
        await queue.consume(self.handle_message)


GetRMQ = Annotated[RMQService, Depends(RMQService)]
