from loguru import logger
from dtos import EmailDTO
from settings import settings


import aiohttp


async def _send(
    email: EmailDTO,
) -> aiohttp.ClientResponse:
    """Send an email."""
    url = f"https://api.mailgun.net/v3/{settings.mailgun.domain}/messages"
    auth = aiohttp.BasicAuth(
        "api",
        settings.mailgun.api_key.get_secret_value(),
    )
    data = {
        "from": f"<Bachelor> {settings.mailgun.from_email}",
        "to": [email.email],
        "subject": email.subject,
        "text": email.body,
        "html": email.html,
    }

    async with (
        aiohttp.ClientSession() as client,
        client.request(
            "POST",
            url,
            auth=auth,
            data=data,
        ) as response,
    ):
        return response


async def send_email(
    email: EmailDTO,
) -> None:
    """Send an email to a given email address."""

    if (
        settings.mailgun.api_key.get_secret_value() == ""
        or settings.mailgun.from_email == ""
    ):
        logger.error("Mailgun configuration is missing")
        return

    response = await _send(email)
    if response.status < 300:
        logger.info(f"Email sent to {email.email}")
        return

    logger.error(f"Failed to send email to {email.email}")
