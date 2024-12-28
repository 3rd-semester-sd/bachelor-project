from enum import StrEnum, auto


class NotificationType(StrEnum):
    """Notification type enum."""

    BOOKING_CONFIRMATION = auto()
    BOOKING_CONFIRMATION_SUCCESS = auto()
    BOOKING_REJECTION = auto()
