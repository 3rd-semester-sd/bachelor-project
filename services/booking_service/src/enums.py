from enum import Enum, auto


class BookingStatus(Enum):
    """Booking status enum."""

    PENDING = auto()
    CONFIRMED = auto()
    CANCELED = auto()
    COMPLETED = auto()
    REJECTED = auto()
