from fastapi import APIRouter
from db.db_dependencies import GetDBSession
import sqlalchemy as sa
from settings import settings
from services.rabbit.dependencies import GetRMQ

from loguru import logger


router = APIRouter()


@router.get("/health")
async def health_check() -> bool:
    """Return True if the service is healthy."""
    return True


@router.get("/db-test")
async def test_jwt(session: GetDBSession) -> None:
    """Test the database connection."""

    logger.info("Testing DB connection")
    logger.info(f"Settings: {settings.pg.__repr__()}")

    query = "SELECT 1"
    await session.execute(sa.text(query))
    logger.info("DB connection successful")

    return None


@router.post("/send-notification")
async def send_notification(rmq: GetRMQ) -> bool:
    """Send a notification."""
    return True
