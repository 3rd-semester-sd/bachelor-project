import asyncio
from uuid import UUID
import daos
from enums import BookingStatus
from loguru import logger
import dtos
from typing import Any, Callable
from services.rabbit.dependencies import RMQService
from services.http_client.dependencies import RestaurantClient


async def delay_task(
    tts: int,
    func: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Delay a task by a certain amount of time.

    Will sleep for `tts` seconds, then call `func` with `args` and `kwargs`.
    """
    await asyncio.sleep(tts)
    await func(*args, **kwargs)


async def verify_booking_status(
    booking_id: UUID,
    r_dao: daos.BookingReadDAO,
    w_dao: daos.BookingWriteDAO,
    rmq: RMQService,
    restaurant_client: RestaurantClient,
) -> None:
    """Verify the status of a booking."""
    db_booking = await r_dao.filter_one(id=booking_id)

    if db_booking is None:
        logger.error(f"Booking {booking_id} not found, during status verification.")
        return

    if db_booking.status == BookingStatus.REJECTED:
        logger.error(f"Booking {booking_id} is rejected.")
        return

    if db_booking.status == BookingStatus.CONFIRMED:
        logger.error(f"Booking {booking_id} is already confirmed.")
        return

    restaurant = await restaurant_client.get_restaurant_by_id(
        restaurant_id=db_booking.restaurant_id,
    )

    # if the booking is still pending, reject it.
    await w_dao.update(
        id=booking_id,
        update_dto=dtos.BookingUpdateDTO(
            status=BookingStatus.REJECTED,
        ),
    )

    await rmq.send_rejection_email(
        email=db_booking.email,
        full_name=db_booking.full_name,
        phone_number=db_booking.phone_number,
        restaurant_name=restaurant.restaurant_name,
        booking_time=db_booking.booking_time,
        number_of_people=db_booking.number_of_people,
    )

    logger.info(f"Booking {booking_id} has been rejected.")


async def demo_task(
    text: str,
) -> None:
    """Demo task."""
    logger.info(f"Demo task: {text}")
