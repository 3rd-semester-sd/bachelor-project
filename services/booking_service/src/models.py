import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from db import Base
from enums import BookingStatus


class Booking(Base):
    """Booking model."""

    __tablename__ = "booking"

    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
    )
    full_name: Mapped[str] = mapped_column(
        sa.String,
    )
    email: Mapped[str] = mapped_column(
        sa.String,
    )
    phone_number: Mapped[str] = mapped_column(
        sa.String,
    )
    booking_date: Mapped[sa.Date] = mapped_column(
        sa.Date,
    )
    booking_time: Mapped[sa.Time] = mapped_column(
        sa.Time,
    )
    number_of_people: Mapped[int] = mapped_column(
        sa.Integer,
    )
    special_request: Mapped[str] = mapped_column(
        sa.String,
    )
    status: Mapped[BookingStatus] = mapped_column(
        sa.Enum(BookingStatus),
        default=BookingStatus.PENDING,
    )
