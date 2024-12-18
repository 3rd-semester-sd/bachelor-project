from fastapi import APIRouter
from db.db_dependencies import GetDBSession
import sqlalchemy as sa
from settings import settings
from services.rabbit.dependencies import GetRMQ
from loguru import logger
import daos
import dtos
import exceptions

base_router = APIRouter(prefix="/api")


##################
# Booking routes #
##################


booking_router = APIRouter(prefix="/booking")


@booking_router.post("")
async def create_booking(
    input_dto: dtos.BookingInputDTO,
    r_dao: daos.GetDAORO,
    w_dao: daos.GetDAO,
    # rmq: GetRMQ,
) -> dtos.DefaultCreatedResponse:
    """Create a booking."""

    try:
        existing_booking = await r_dao.filter_one(
            restaurant_id=input_dto.restaurant_id,
            email=input_dto.email,
        )
    except Exception as e:
        logger.error(e)
        return

    if existing_booking is not None:
        raise exceptions.Http403("Booking already exists.")

    obj_id = await w_dao.create(input_dto=input_dto)

    # TODO:
    # - Store token in redis(?) with 15 minutes expiry
    # - Send email to the user containing the token
    # - Send notification to the restaurant (maybe)
    # - If the user doesn't confirm the booking within 15 minutes, delete the token
    #   and set the booking status to cancelled
    # - If the user confirms the booking, set the booking status to confirmed, and
    #   delete the token

    return dtos.DefaultCreatedResponse(
        data=dtos.CreatedResponse(id=obj_id),
    )


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
async def test_jwt(session: GetDBSession) -> None:
    """Test the database connection."""

    logger.info("Testing DB connection")
    logger.info(f"Settings: {settings.pg.__repr__()}")

    query = "SELECT 1"
    await session.execute(sa.text(query))
    logger.info("DB connection successful")

    return None
