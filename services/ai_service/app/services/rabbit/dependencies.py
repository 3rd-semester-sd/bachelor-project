from typing import Annotated
from aio_pika import DeliveryMode, ExchangeType, IncomingMessage, Message
from aio_pika import Channel
from aio_pika.pool import Pool
from fastapi import Depends, Request, logger
from openai import AsyncAzureOpenAI


from app.services.es.dependencies import ElasticsearchService
from app.services.azure_ai.embeddings import generate_restaurant_embedding
from app.api.dtos.dtos import RestaurantRabbitInputDTO


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

        If the embedding succeeds a message is published to `embedding_result_exchange`,
        informing the consumer if the embedding operation succeded or failed.
        """

        async with message.process():
            body_str = message.body.decode("utf-8")
            data = RestaurantRabbitInputDTO.model_validate_json(body_str)
            try:
                # generate embedding based on input
                await generate_restaurant_embedding(
                    data, self.ai_client, self.es_service
                )
                # publish success
                data.result = "success"
                await self.publish_result(data=data)
            except Exception as e:
                # publish fail
                error_message = f"Error processing message: {e}"
                await self.publish_result(data=data, error_message=error_message)
                logger.logger.error(error_message)

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

    async def publish_result(
        self,
        data: RestaurantRabbitInputDTO,
        error_message: str | None = None,
    ):
        """
        Publishes a success/failure event back to the Restaurant Service.
        """
        async with self.pool.acquire() as connection:
            exchange_name = "embedding_result_exchange"
            exchange = await connection.declare_exchange(
                exchange_name, ExchangeType.FANOUT, durable=True
            )

            if error_message:
                data.error = error_message

            payload = data.model_dump_json()
            await exchange.publish(
                Message(
                    payload.encode("utf-8"),
                    content_type="application/json",
                    delivery_mode=DeliveryMode.PERSISTENT,
                ),
                routing_key="",
            )


GetRMQ = Annotated[RMQService, Depends(RMQService)]
