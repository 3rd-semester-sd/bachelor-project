from datetime import datetime
from typing import Annotated, Literal

from aio_pika import Channel, Message
from aio_pika.pool import Pool
from fastapi import Depends, Request
from pydantic import BaseModel
from datetime import timezone
from pydantic import computed_field


class _BaseRMQPublishDTO(BaseModel):
    """Base model for publishing messages."""

    from_service: str

    @computed_field  # type: ignore
    @property
    def created_at(self) -> datetime:
        """Get current datetime."""
        return datetime.now(timezone.utc)


class SendEmailDTO(_BaseRMQPublishDTO):
    """Send email DTO."""

    email: str
    full_name: str
    business_name: str
    business_type: Literal["restaurant"]


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

    async def _publish(
        self,
        routing_key: str,
        message: BaseModel,
    ) -> None:
        """Publish message to a specific routing key."""

        async with self.pool.acquire() as conn:
            exchange = await conn.declare_exchange(
                name="bachelor_exchange",
                auto_delete=True,
            )
            await exchange.publish(
                message=Message(
                    body=message.model_dump_json().encode("utf-8"),
                    content_encoding="utf-8",
                    content_type="application/json",
                ),
                routing_key=routing_key,
            )

    async def send_email(self, email: str, full_name: str, business_name: str) -> None:
        """Send email to the user."""
        await self._publish(
            routing_key="send_email",
            message=SendEmailDTO(
                email=email,
                full_name=full_name,
                business_name=business_name,
                business_type="restaurant",
                from_service="booking_service",
            ),
        )


GetRMQ = Annotated[RMQService, Depends(RMQService)]
