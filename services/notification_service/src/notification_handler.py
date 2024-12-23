from enums import NotificationType

from abc import ABC, abstractmethod
from typing import ClassVar, Any
from pydantic import BaseModel
from services.email_service import email_service
from dtos import EmailDTO


class NotificationRequestDTO(BaseModel):
    """Notification request DTO."""

    notification_type: NotificationType
    payload: dict[str, Any]


class NotificationHandler(ABC):
    handlers: ClassVar[dict[str, "type[NotificationHandler]"]] = {}

    def __init_subclass__(cls, notification_type: str) -> None:
        cls.handlers[notification_type] = cls
        super().__init_subclass__()

    @classmethod
    def get_handler(
        cls,
        notification_type: str,
    ) -> "type[NotificationHandler] | None":
        """Get handler for notification type."""
        return cls.handlers.get(notification_type)

    @abstractmethod
    async def handle(self, data: NotificationRequestDTO) -> None:
        """Handle notification."""


class BookingConfirmationHandler(
    NotificationHandler,
    notification_type=NotificationType.BOOKING_CONFIRMATION,
):
    async def handle(self, data: NotificationRequestDTO) -> None:
        """Handle booking confirmation notification."""

        payload = data.payload

        full_name = payload["full_name"]
        booking_time = payload["booking_time"]
        confirmation_code = payload["confirmation_code"]
        restaurant_name = payload["restaurant_name"]
        number_of_people = payload["number_of_people"]

        subject = "Booking Confirmation"
        body = f"""
            Hello {full_name},
            You have booked a table at {restaurant_name} 
            for {number_of_people} guests on {booking_time}.
            This is your confirmation code: {confirmation_code}
            Use it within 15 minutes to confirm your booking.
            
            Thank you!
        """
        html = f"""
            <h1>Booking Confirmation</h1>
            <p>Hello {full_name},</p>
            <p>
                You have booked a table at {restaurant_name} 
                for {number_of_people} guests on {booking_time}.
            </p>
            <p>This is your confirmation code: <b>{confirmation_code}</b></p>
            <br>
            <p>Use it within 15 minutes to confirm your booking.</p>
            <p>Thank you!</p>

        """

        await email_service.send_email(
            email=EmailDTO(
                email=payload["email"],
                subject=subject,
                body=body,
                html=html,
            )
        )


class BookingConfirmationSuccessHandler(
    NotificationHandler,
    notification_type=NotificationType.BOOKING_CONFIRMATION_SUCCESS,
):

    async def handle(self, data: NotificationRequestDTO) -> None:
        """Handle booking confirmation success notification."""

        payload = data.payload

        full_name = payload["full_name"]
        booking_time = payload["booking_time"]
        restaurant_name = payload["restaurant_name"]
        number_of_people = payload["number_of_people"]

        subject = "Booking Confirmed"
        body = f"""
            Hello {full_name},
            Your booking at {restaurant_name} for {number_of_people} 
            guests on {booking_time} has been confirmed.
            
            See you soon!
        """
        html = f"""
            <h1>Booking Confirmed</h1>
            <p>Hello {full_name},</p>
            <p>Your booking at {restaurant_name} for {number_of_people} 
            guests on {booking_time} has been confirmed.</p>
            <br>
            <p>See you soon!</p>
        """

        await email_service.send_email(
            email=EmailDTO(
                email=payload["email"],
                subject=subject,
                body=body,
                html=html,
            )
        )


class BookingRejectionHandler(
    NotificationHandler,
    notification_type=NotificationType.BOOKING_REJECTION,
):

    async def handle(self, data: NotificationRequestDTO) -> None:
        """Handle booking rejection notification."""

        payload = data.payload

        full_name = payload["full_name"]
        booking_time = payload["booking_time"]
        restaurant_name = payload["restaurant_name"]
        number_of_people = payload["number_of_people"]

        subject = "Booking Rejected"
        body = f"""
            Hello {full_name},
            Your booking at {restaurant_name} for {number_of_people} 
            guests on {booking_time} has been rejected by the restaurant,
            or the booking time has passed.

            Please try again.
        """
        html = f"""
            <h1>Booking Rejected</h1>
            <p>Hello {full_name},</p>
            <p>Your booking at {restaurant_name} for {number_of_people}
            guests on {booking_time} has been rejected by the restaurant,
            or the booking time has passed.</p>
            <br>
            <p>Please try again.</p>
        """

        await email_service.send_email(
            email=EmailDTO(
                email=payload["email"],
                subject=subject,
                body=body,
                html=html,
            )
        )
