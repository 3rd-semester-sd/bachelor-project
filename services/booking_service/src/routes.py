from fastapi import APIRouter

from enums import BookingStatus
from services.rabbit.dependencies import GetRMQ
import daos
import dtos
import exceptions
from uuid import UUID
from services.redis.dependencies import GetRedis
from datetime import datetime
from constants import BOOKING_CONFIRMATION_EXPIRE_SECONDS
from fastapi import BackgroundTasks
import tasks

import utils

base_router_v1 = APIRouter(prefix="/api/v1")


##################
# Booking routes #
##################


booking_router = APIRouter(prefix="/booking")


def _validate_booking_time(
    input_dto: dtos.BookingInputDTO,
    open_days: tuple[int, ...],
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


async def _validate_booking_overlap(
    r_dao: daos.GetDAORO,
    email: str,
    restaurant_id: UUID,
    booking_time: datetime,
    reservation_time_hr: int,
) -> None:
    """Check if a booking exists for the email in the last n hours."""
    if await r_dao.check_duplicate_booking(
        email=email,
        restaurant_id=restaurant_id,
        booking_time=booking_time,
        reservation_time_hr=reservation_time_hr,
    ):
        raise exceptions.Http403(
            f"Cannot book another table within {reservation_time_hr} hours."
        )


@booking_router.post("")
async def create_booking(
    input_dto: dtos.BookingInputDTO,
    r_dao: daos.GetDAORO,
    w_dao: daos.GetDAO,
    rmq: GetRMQ,
    redis: GetRedis,
    background_tasks: BackgroundTasks,
) -> dtos.DefaultCreatedResponse:
    """Create a booking."""

    # TODO: get these details from restaurant service by id
    max_seats = 30
    opening_hr, closing_hr = (10, 22)
    open_days = (1, 1, 1, 1, 1, 1, 0)
    reservation_time_hr = 2
    closing_time_buffer_hr = 2
    restaurant_name = "Test Restaurant"

    _validate_booking_time(
        input_dto,
        open_days,
        opening_hr,
        closing_hr,
        closing_time_buffer_hr,
    )

    await _validate_booking_overlap(
        r_dao=r_dao,
        email=input_dto.email,
        restaurant_id=input_dto.restaurant_id,
        booking_time=input_dto.booking_time,
        reservation_time_hr=reservation_time_hr,
    )

    await _validate_seat_availability(
        r_dao=r_dao,
        input_dto=input_dto,
        max_seats=max_seats,
        reservation_time_hr=reservation_time_hr,
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
        restaurant_name=restaurant_name,
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
    )

    return dtos.DefaultCreatedResponse(
        data=dtos.CreatedResponse(id=booking_id),
    )


@booking_router.patch("/{confirmation_code}")
async def confirm_booking(
    confirmation_code: str,
    r_dao: daos.GetDAORO,
    w_dao: daos.GetDAO,
    redis: GetRedis,
    rmq: GetRMQ,
    background_tasks: BackgroundTasks,
) -> None:
    """Confirm a booking."""

    redis_key = utils.redis_confirmation_key(confirmation_code)
    val = await redis.get(redis_key)

    if not val:
        raise exceptions.Http403("Invalid confirmation code, or expired.")

    booking_id = UUID(val.decode())

    db_booking = await r_dao.filter_one(id=booking_id)

    if db_booking is None:
        raise exceptions.Http404("Booking not found.")

    if db_booking.status != BookingStatus.PENDING:
        raise exceptions.Http403("Cannot confirm non-pending booking.")

    # TODO: get restaurant from restaurant service
    restaurant_name = "Test Restaurant"

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
        restaurant_name=restaurant_name,
        booking_time=db_booking.booking_time,
        number_of_people=db_booking.number_of_people,
    )


@booking_router.get("/{booking_id}")
async def get_booking(
    booking_id: UUID,
    r_dao: daos.GetDAORO,
) -> dtos.DataResponse[dtos.BookingDTO]:
    """Get a booking."""

    db_booking = await r_dao.filter_one(id=booking_id)

    if db_booking is None:
        raise exceptions.Http404("Booking not found.")

    return dtos.DataResponse(
        data=dtos.BookingDTO.model_validate(db_booking),
    )


@booking_router.get("")
async def get_booking_list(
    r_dao: daos.GetDAORO,
    pagination: dtos.Pagination,
) -> dtos.OffsetResults[dtos.BookingDTO]:
    """Get bookings."""

    results = await r_dao.get_offset_results(
        out_dto=dtos.BookingDTO,
        pagination=pagination,
    )

    return results


base_router_v1.include_router(booking_router)


#################
# Health routes #
#################


@base_router_v1.get("/health")
async def health_check() -> bool:
    """Return True if the service is healthy."""

    return True


###############
# Demo routes #
###############

demo_router = APIRouter(prefix="/demo")


@demo_router.post("/send-notification")
async def send_notification(rmq: GetRMQ) -> bool:
    """Send a notification."""

    await rmq.send_confirmation_email(
        email="martin_laursen9@hotmail.com",
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


base_router_v1.include_router(demo_router)
