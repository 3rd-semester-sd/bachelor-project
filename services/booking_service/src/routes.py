from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPBearer
from typing import Annotated

from enums import BookingStatus
from services.rabbit.dependencies import GetRMQ
from services.http_client.dependencies import GetRestaurantClient
import daos
import dtos
import exceptions
from models import Booking
from uuid import UUID
from services.redis.dependencies import GetRedis
from datetime import datetime
from constants import BOOKING_CONFIRMATION_EXPIRE_SECONDS
from fastapi import BackgroundTasks
import tasks
import sqlalchemy as sa
from loguru import logger

import utils

security = HTTPBearer()
Auth = Annotated[str, Depends(security)]

base_router = APIRouter(prefix="/api")
base_router_v1 = APIRouter(prefix="/v1")


##################
# Booking routes #
##################


booking_router = APIRouter(prefix="/bookings")


def _validate_booking_time(
    input_dto: dtos.BookingInputDTO,
    open_days: list[int],
    opening_hr: int,
    closing_hr: int,
    closing_time_buffer_hr: int,
) -> None:
    """Validate the booking time."""
    if open_days[input_dto.booking_time.weekday()] == 0:
        raise exceptions.Http403("Cannot book on this day.")

    if (
        input_dto.booking_time.hour < opening_hr
        or input_dto.booking_time.hour > closing_hr
    ):
        raise exceptions.Http403("Cannot book at this time.")

    latest_booking_time = closing_hr - closing_time_buffer_hr
    if input_dto.booking_time.hour > latest_booking_time:
        raise exceptions.Http403(
            f"Bookings must be made before {latest_booking_time}:00 "
            "to allow for closing."
        )


async def _validate_seat_availability(
    r_dao: daos.GetDAORO,
    input_dto: dtos.BookingInputDTO,
    max_seats: int,
    reservation_time_hr: int,
) -> None:
    """Validate seat availability."""
    bookings_count = await r_dao.count_booked_seats_during_time(
        restaurant_id=input_dto.restaurant_id,
        booking_time=input_dto.booking_time,
        reservation_time_hr=reservation_time_hr,
    )

    if bookings_count + input_dto.number_of_people > max_seats:
        raise exceptions.Http403("Not enough seats available.")


async def _ensure_no_overlap_in_bookings(
    r_dao: daos.GetDAORO,
    email: str,
    restaurant_id: UUID,
    booking_time: datetime,
    reservation_time_hr: int,
) -> None:
    """Ensure no overlap in bookings."""
    if await r_dao.check_duplicate_booking(
        email=email,
        restaurant_id=restaurant_id,
        booking_time=booking_time,
        reservation_time_hr=reservation_time_hr,
    ):
        raise exceptions.Http403(
            f"Cannot book another table within {reservation_time_hr} hours."
        )


@booking_router.post("", status_code=201)
async def create_booking(
    input_dto: dtos.BookingInputDTO,
    restaurant_client: GetRestaurantClient,
    r_dao: daos.GetDAORO,
    w_dao: daos.GetDAO,
    rmq: GetRMQ,
    redis: GetRedis,
    background_tasks: BackgroundTasks,
) -> dtos.DefaultCreatedResponse:
    """Create a booking."""

    restaurant_data = await restaurant_client.get_restaurant_by_id(
        restaurant_id=input_dto.restaurant_id,
    )
    restaurant_settings = restaurant_data.restaurant_settings

    _validate_booking_time(
        input_dto,
        restaurant_settings.open_days,
        restaurant_settings.opening_hr,
        restaurant_settings.closing_hr,
        restaurant_settings.closing_time_buffer_hr,
    )

    await _ensure_no_overlap_in_bookings(
        r_dao=r_dao,
        email=input_dto.email,
        restaurant_id=input_dto.restaurant_id,
        booking_time=input_dto.booking_time,
        reservation_time_hr=restaurant_settings.reservation_time_hr,
    )

    await _validate_seat_availability(
        r_dao=r_dao,
        input_dto=input_dto,
        max_seats=restaurant_settings.max_seats,
        reservation_time_hr=restaurant_settings.reservation_time_hr,
    )

    booking_id = await w_dao.create(input_dto=input_dto)
    confirmation_code = utils.generate_confirmation_code()

    # store the confirmation code in redis
    await redis.set(
        utils.redis_confirmation_key(confirmation_code),
        str(booking_id),
        ex=BOOKING_CONFIRMATION_EXPIRE_SECONDS,
    )

    # notify the user that their booking has been received
    background_tasks.add_task(
        rmq.send_confirmation_email,
        email=input_dto.email,
        full_name=input_dto.full_name,
        phone_number=input_dto.phone_number,
        restaurant_name=restaurant_data.restaurant_name,
        booking_time=input_dto.booking_time,
        confirmation_code=confirmation_code,
        number_of_people=input_dto.number_of_people,
    )

    # verify the booking status after 15 minutes
    background_tasks.add_task(
        tasks.delay_task,
        BOOKING_CONFIRMATION_EXPIRE_SECONDS,
        tasks.verify_booking_status,
        booking_id=booking_id,
        r_dao=r_dao,
        w_dao=w_dao,
        rmq=rmq,
        restaurant_client=restaurant_client,
    )

    logger.info(f"* TEMPORARY * - Confirmation Code: {confirmation_code}")

    return dtos.DefaultCreatedResponse(
        data=dtos.CreatedResponse(id=booking_id),
    )


@booking_router.patch("/{confirmation_code}")
async def confirm_booking(
    confirmation_code: str,
    restaurant_client: GetRestaurantClient,
    r_dao: daos.GetDAORO,
    w_dao: daos.GetDAO,
    redis: GetRedis,
    rmq: GetRMQ,
    background_tasks: BackgroundTasks,
) -> dtos.ValueResponse[bool]:
    """Confirm a booking."""

    redis_key = utils.redis_confirmation_key(confirmation_code)
    val = await redis.get(redis_key)

    if not val:
        raise exceptions.Http403("Invalid confirmation code, or expired.")

    try:
        booking_id = UUID(val.decode())
    except ValueError:
        raise exceptions.Http403("Unexpected error.")

    db_booking = await r_dao.filter_one(id=booking_id)

    if db_booking is None:
        raise exceptions.Http404("Booking not found.")

    if db_booking.status != BookingStatus.PENDING:
        raise exceptions.Http403("Cannot confirm non-pending booking.")

    restaurant = await restaurant_client.get_restaurant_by_id(
        restaurant_id=db_booking.restaurant_id,
    )

    await w_dao.update(
        id=booking_id,
        update_dto=dtos.BookingUpdateDTO(
            status=BookingStatus.CONFIRMED,
        ),
    )

    await redis.delete(redis_key)

    # notify the user that their booking has been confirmed
    background_tasks.add_task(
        rmq.send_confirmation_success_email,
        email=db_booking.email,
        full_name=db_booking.full_name,
        phone_number=db_booking.phone_number,
        restaurant_name=restaurant.restaurant_name,
        booking_time=db_booking.booking_time,
        number_of_people=db_booking.number_of_people,
    )

    return dtos.ValueResponse(data=True)


def _get_x_user_id(request: Request) -> UUID:
    """Get the user ID from the request headers."""
    try:
        return UUID(request.headers.get("x-user-id"))
    except ValueError:
        raise exceptions.Http403("Invalid user ID.")


@booking_router.get("/protected/{booking_id}")
async def get_booking(
    booking_id: UUID,
    request: Request,
    restaurant_client: GetRestaurantClient,
    r_dao: daos.GetDAORO,
    _: Auth,
) -> dtos.DataResponse[dtos.BookingDTO]:
    """Get a booking."""

    db_booking = await r_dao.filter_one(id=booking_id)

    if db_booking is None:
        raise exceptions.Http404("Booking not found.")

    await restaurant_client.verify_membership(
        user_id=_get_x_user_id(request),
        restaurant_id=db_booking.restaurant_id,
    )

    return dtos.DataResponse(
        data=dtos.BookingDTO.model_validate(db_booking),
    )


@booking_router.get("/protected/restaurant/{restaurant_id}")
async def get_bookings_by_restaurant(
    restaurant_id: UUID,
    request: Request,
    r_dao: daos.GetDAORO,
    restaurant_client: GetRestaurantClient,
    pagination: dtos.Pagination,
    _: Auth,
) -> dtos.OffsetResults[dtos.BookingDTO]:
    """Get bookings by restaurant."""

    await restaurant_client.verify_membership(
        user_id=_get_x_user_id(request),
        restaurant_id=restaurant_id,
    )

    results = await r_dao.get_offset_results(
        out_dto=dtos.BookingDTO,
        pagination=pagination,
        query=sa.select(Booking).where(
            Booking.restaurant_id == restaurant_id,
        ),
    )

    return results


base_router_v1.include_router(booking_router)
base_router.include_router(base_router_v1)


#################
# Health routes #
#################


@base_router.get("/health")
async def health_check() -> bool:
    """Return True if the service is healthy."""

    return True


###############
# Demo routes #
###############

demo_router = APIRouter(prefix="/demo")


@demo_router.post("/send-notification", status_code=201)
async def send_notification(rmq: GetRMQ) -> bool:
    """Send a notification."""

    await rmq.send_confirmation_email(
        email="martin_laursen21@hotmail.com",
        full_name="Martin Laursen",
        restaurant_name="Applebee's",
        booking_time=datetime.now(),
        confirmation_code="AS3F2Z",
        number_of_people=4,
        phone_number="1234567890",
    )

    return True


@demo_router.post("/demo-task")
async def demo_task(
    tts: int,
    text: str,
    background_tasks: BackgroundTasks,
) -> None:
    """Demo task."""

    background_tasks.add_task(
        tasks.delay_task,
        tts,
        tasks.demo_task,
        text,
    )


base_router.include_router(demo_router)
