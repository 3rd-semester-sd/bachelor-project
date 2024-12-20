from fastapi import APIRouter

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


#################
# Notification routes #
#################


@base_router.post("/notification")
async def email():
    """Send an email."""

    email = EmailDTO(
        email="martin_laursen9@hotmail.com",
        subject="Hello",
        body="Testing sos!",
        html="<h1>Testiness!</h1>",
    )

    await email_service.send_email(email)
