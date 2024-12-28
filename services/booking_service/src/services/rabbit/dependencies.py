from datetime import datetime
from typing import Annotated

from aio_pika import Channel, Message
from aio_pika.pool import Pool
from fastapi import Depends, Request
from pydantic import BaseModel
from enums import NotificationType
import dtos


def get_rmq_channel_pool(request: Request) -> Pool[Channel]:  # pragma: no cover
    """
    Get channel pool from the state.

    :param request: current request.
    :return: channel pool.
    """
    return request.app.state.rmq_channel_pool


GetRMQChannelPool = Annotated[Pool[Channel], Depends(get_rmq_channel_pool)]


class RMQService:
    """RabbitMQ Service."""

    def __init__(
        self,
        pool: GetRMQChannelPool,
    ) -> None:
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

    async def send_confirmation_email(
        self,
        email: str,
        full_name: str,
        phone_number: str,
        restaurant_name: str,
        booking_time: datetime,
        confirmation_code: str,
        number_of_people: int,
    ) -> None:
        """Send email to the user."""

        await self._publish(
            routing_key="send_notification_queue",
            message=dtos.BookingEmailDTO(
                notification_type=NotificationType.BOOKING_CONFIRMATION,
                payload=dtos.BookingConfirmationPayload(
                    email=email,
                    full_name=full_name,
                    phone_number=phone_number,
                    restaurant_name=restaurant_name,
                    booking_time=booking_time,
                    confirmation_code=confirmation_code,
                    number_of_people=number_of_people,
                ),
            ),
        )

    async def send_confirmation_success_email(
        self,
        email: str,
        full_name: str,
        phone_number: str,
        restaurant_name: str,
        booking_time: datetime,
        number_of_people: int,
    ) -> None:
        """Send email to the user."""

        await self._publish(
            routing_key="send_notification_queue",
            message=dtos.BookingEmailDTO(
                notification_type=NotificationType.BOOKING_CONFIRMATION_SUCCESS,
                payload=dtos.BookingConfirmationSuccessPayload(
                    email=email,
                    full_name=full_name,
                    phone_number=phone_number,
                    restaurant_name=restaurant_name,
                    booking_time=booking_time,
                    number_of_people=number_of_people,
                ),
            ),
        )

    async def send_rejection_email(
        self,
        email: str,
        full_name: str,
        phone_number: str,
        restaurant_name: str,
        booking_time: datetime,
        number_of_people: int,
    ) -> None:
        """Send email to the user."""

        await self._publish(
            routing_key="send_notification_queue",
            message=dtos.BookingEmailDTO(
                notification_type=NotificationType.BOOKING_REJECTION,
                payload=dtos.BookingRejectionPayload(
                    email=email,
                    full_name=full_name,
                    phone_number=phone_number,
                    restaurant_name=restaurant_name,
                    booking_time=booking_time,
                    number_of_people=number_of_people,
                ),
            ),
        )


GetRMQ = Annotated[RMQService, Depends(RMQService)]
