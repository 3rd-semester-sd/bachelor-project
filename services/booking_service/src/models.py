from datetime import datetime
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
    booking_time: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
    )
    number_of_people: Mapped[int] = mapped_column(sa.Integer())
    special_request: Mapped[str] = mapped_column(
        sa.String,
    )
    status: Mapped[BookingStatus] = mapped_column(
        sa.Enum(BookingStatus, name="booking_status"),
        default=BookingStatus.PENDING,
    )

    __table_args__ = (
        sa.CheckConstraint(
            "booking_time > now()", name="booking_time_gt_now_constraint"
        ),
        sa.Index("booking_restaurant_id_idx", "restaurant_id"),
    )
