from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Annotated
from uuid import UUID
import enums
from fastapi import Depends
from pydantic import Field

from datetime import timezone
from enums import NotificationType
from pydantic import computed_field


# Base
class BaseOrmModel(BaseModel):
    """BaseOrmModel."""

    model_config = ConfigDict(from_attributes=True)


# Pagination


class PaginationParams(BaseModel):
    """DTO for offset pagination."""

    offset: int = Field(0, ge=0)
    limit: int = Field(20, le=20, ge=1)


class OffsetResults[T: BaseModel](BaseModel):
    """DTO for offset paginated response."""

    data: list[T]


Pagination = Annotated[PaginationParams, Depends(PaginationParams)]

# Response


class CreatedResponse(BaseModel):
    """Response model for created objects."""

    id: UUID = Field(..., description="ID of the created object.")


class DefaultCreatedResponse(BaseModel):
    """Default response model for created objects."""

    data: CreatedResponse
    success: bool = True
    message: str | None = "Object was created!"


class DataResponse[T: BaseModel](BaseModel):
    """Default response model returning only data."""

    data: T | None = None


class ValueResponse[T: str | int | bool](BaseModel):
    """Default response model returning only a value."""

    data: T | None = None


#############
# Core DTOs #
#############


class _BookingBaseDTO(BaseOrmModel):
    """Base DTO for booking."""

    restaurant_id: UUID
    full_name: str
    email: str
    phone_number: str
    booking_time: datetime = Field(..., gt=datetime.now())
    number_of_people: int = Field(..., ge=1)
    special_request: str


class BookingInputDTO(_BookingBaseDTO):
    """DTO for creating a booking."""


class BookingUpdateDTO(BaseOrmModel):
    """DTO for updating a booking."""

    booking_time: datetime | None = None
    number_of_people: int | None = None
    special_request: str | None = None
    status: enums.BookingStatus | None = None


class BookingDTO(_BookingBaseDTO):
    """DTO for booking."""


#################
# RabbitMQ DTOs #
#################


class _BaseRMQPublishDTO(BaseModel):
    """Base model for publishing messages."""

    from_service: str = "booking_service"

    @computed_field  # type: ignore
    @property
    def created_at(self) -> datetime:
        """Get current datetime."""
        return datetime.now(timezone.utc)


class _BaseNotificationDTO(_BaseRMQPublishDTO):
    """Base notification DTO."""

    notification_type: NotificationType = NotificationType.BOOKING_CONFIRMATION


class _BaseBookingPayload(BaseModel):
    """Base booking payload."""

    email: str
    full_name: str
    phone_number: str
    restaurant_name: str
    booking_time: datetime
    number_of_people: int


class BookingConfirmationPayload(_BaseBookingPayload):
    """Booking confirmation payload."""

    confirmation_code: str


class BookingConfirmationSuccessPayload(_BaseBookingPayload):
    """Booking confirmation success payload."""


class BookingRejectionPayload(_BaseBookingPayload):
    """Booking rejection payload."""


BookingPayloadType = (
    BookingConfirmationPayload
    | BookingConfirmationSuccessPayload
    | BookingRejectionPayload
)


class BookingEmailDTO[PayloadT: BookingPayloadType](_BaseNotificationDTO):
    """Send booking email DTO, with payload."""

    payload: PayloadT
