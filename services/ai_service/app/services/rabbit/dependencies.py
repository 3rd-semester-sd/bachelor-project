from typing import Annotated
from aio_pika import ExchangeType, IncomingMessage
from aio_pika import Channel
from aio_pika.pool import Pool
from fastapi import Depends, Request, logger
from openai import AsyncAzureOpenAI


from app.services.es.dependencies import ElasticsearchService
from app.services.azure_ai.embeddings import generate_restaurant_embedding
from app.api.dtos.dtos import RestaurantInputDTO


def get_rmq_channel_pool(request: Request) -> Pool[Channel]:
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
        """
        Function that handles incoming messages from the queue.
        When a message is received, it gets parsed then processed,
        further in the embedding function.
        """

        async with message.process():
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
        Declare the exchange and queue, and start consuming it.
        When a message is received it gets handled accordingly.
        """

        async with self.pool.acquire() as conn:
            exchange_name = "new_restaurant_exchange"
            exchange_type = ExchangeType.FANOUT

            exchange = await conn.declare_exchange(
                exchange_name,
                exchange_type,
                durable=True,
            )
            queue_name = "new_restaurant_queue"
            queue = await conn.declare_queue(queue_name, durable=True)
            # bind queue
            await queue.bind(exchange=exchange, routing_key="")
            # start consuming
            await queue.consume(self.handle_message)


GetRMQ = Annotated[RMQService, Depends(RMQService)]
