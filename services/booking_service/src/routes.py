from fastapi import APIRouter

from services.booking_service.src.enums import BookingStatus
from services.rabbit.dependencies import GetRMQ
import daos
import dtos
import exceptions
from uuid import uuid4, UUID
import random
import string
from services.redis.dependencies import GetRedis

base_router = APIRouter(prefix="/api")


##################
# Booking routes #
##################


booking_router = APIRouter(prefix="/booking")


def _redis_confirmation_key(confirmation_code: str) -> str:
    return f"booking:{confirmation_code}:confirmation_code"


@booking_router.post("")
async def create_booking(
    input_dto: dtos.BookingInputDTO,
    r_dao: daos.GetDAORO,
    w_dao: daos.GetDAO,
    # rmq: GetRMQ,
    redis: GetRedis,
) -> dtos.DefaultCreatedResponse:
    """Create a booking."""

    # TODO: get these details from restaurant service by id
    max_seats = 30
    opening_hr, closing_hr = (10, 22)
    open_days = (1, 1, 1, 1, 1, 1, 0)
    reservation_time_hr = 2
    closing_time_buffer_hr = 2

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

    # check if same email has already booked a table in the last 2 hours
    if await r_dao.check_duplicate_booking(
        email=input_dto.email,
        restaurant_id=input_dto.restaurant_id,
        booking_time=input_dto.booking_time,
        reservation_time_hr=reservation_time_hr,
    ):
        raise exceptions.Http403(
            f"Cannot book another table within {reservation_time_hr} hours."
        )

    bookings_count = await r_dao.count_booked_seats_during_time(
        restaurant_id=input_dto.restaurant_id,
        booking_time=input_dto.booking_time,
        reservation_time_hr=reservation_time_hr,
    )

    if bookings_count + input_dto.number_of_people > max_seats:
        raise exceptions.Http403("Not enough seats available.")

    # creates the booking with status `PENDING`
    obj_id = await w_dao.create(input_dto=input_dto)

    confirmation_code = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=5)
    )

    # store the confirmation code in redis, with 15 minutes expiry
    await redis.set(
        _redis_confirmation_key(confirmation_code),
        str(obj_id),
        ex=60 * 15,
    )

    # schedule a task to cancel the booking if not confirmed within 15 minutes

    # send email to the user with the confirmation code
    # await rmq.send_email(

    return dtos.DefaultCreatedResponse(
        data=dtos.CreatedResponse(id=obj_id),
    )


@booking_router.patch("/{confirmation_code}")
async def confirm_booking(
    confirmation_code: str,
    dao: daos.GetDAO,
    redis: GetRedis,
) -> None:
    """Confirm a booking."""

    redis_key = _redis_confirmation_key(confirmation_code)
    booking_id = await redis.get(redis_key)

    if not booking_id:
        raise exceptions.Http404("Confirmation code not found.")

    await dao.update(
        id=UUID(booking_id),
        update_dto=dtos.BookingUpdateDTO(status=BookingStatus.CONFIRMED),
    )

    await redis.delete(redis_key)


base_router.include_router(booking_router)


#################
# Health routes #
#################


@base_router.get("/health")
async def health_check() -> bool:
    """Return True if the service is healthy."""
    return True


# Testing


@base_router.post("/send-notification")
async def send_notification(rmq: GetRMQ) -> bool:
    """Send a notification."""

    await rmq.send_email("test", "test", "test")

    return True


@base_router.get("/db-test")
async def test_db(dao: daos.GetDAO) -> str:
    """Test the database connection."""
    import datetime

    id = await dao.create(
        input_dto=dtos.BookingInputDTO(
            restaurant_id=uuid4(),
            full_name="Martin Laursen",
            email="martin@intree.com",
            phone_number="12345678",
            booking_date=(datetime.datetime.now() + datetime.timedelta(days=1)).date(),
            number_of_people=3,
            special_request="Test",
        ),
    )

    return str(id)


@base_router.get("/db-test-read/{id}")
async def test_db_read(id: UUID, dao: daos.GetDAORO) -> None:
    """Test the database connection."""

    booking = await dao.filter_one(id=id)

    print(booking.__dict__)
