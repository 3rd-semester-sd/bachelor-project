from fastapi import APIRouter, Request
from loguru import logger
from services.email_service import email_service
from dtos import EmailDTO


base_router = APIRouter(prefix="/api")


#################
# Health routes #
#################


@base_router.get("/health")
async def health_check() -> bool:
    """Return True if the service is healthy."""
    return True


@base_router.get("/protected/authsvc")
async def test_authsvc(request: Request) -> bool:
    """Test authsvc."""
    logger.info(f"Request: {request.headers}")
    return True


@base_router.get("/send-notification-demo")
async def send_notification_demo(email: str) -> None:
    """Send a notification."""
    email_dto = EmailDTO(
        email=email,
        subject="Test email",
        body="This is a test email",
        html="<h1>This is a test email</h1>",
    )
    await email_service.send_email(email=email_dto)
