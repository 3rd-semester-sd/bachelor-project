from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Annotated, Generic, TypeVar
from uuid import UUID
import enums
from fastapi import Depends
from pydantic import Field


# Base
class BaseOrmModel(BaseModel):
    """BaseOrmModel."""

    model_config = ConfigDict(from_attributes=True)


# Pagination


class PaginationParams(BaseModel):
    """DTO for offset pagination."""

    offset: int = Field(0, ge=0)
    limit: int = Field(20, le=20, ge=1)


DataT = TypeVar("DataT", bound=BaseModel)


class OffsetResults(BaseModel, Generic[DataT]):
    """DTO for offset paginated response."""

    data: list[DataT]


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
