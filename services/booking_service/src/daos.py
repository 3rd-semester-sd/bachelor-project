from fastapi import Depends
from db.db_dependencies import GetDBSessionRO, GetDBSession

from typing import Annotated, Any, TypeVar
from uuid import UUID, uuid4

import sqlalchemy as sa


from dtos import BookingInputDTO, BookingUpdateDTO
from models import Booking
from pydantic import BaseModel
import datetime
from sqlalchemy import orm

import exceptions
from datetime import timedelta
from models import Base
from enums import BookingStatus


Model = TypeVar("Model", bound=Base)
InputDTO = TypeVar("InputDTO", bound=BaseModel)
OutputDTO = TypeVar("OutputDTO", bound=BaseModel)

LoadType = orm.interfaces.LoaderOption | orm.InstrumentedAttribute  # type: ignore
# PaginationType = PaginationParams


class BookingReadDAO:
    """Class for accessing Booking table READ."""

    def __init__(self, session: GetDBSessionRO):
        self.session = session

    async def get_by_id_or_error(
        self,
        id: UUID,
        loads: list[LoadType] | None = None,
        exception: Exception | None = None,
    ) -> Booking:
        """Get a record by ID."""

        query = sa.select(Booking).where(Booking.id == id)

        if loads:
            query = self._eager_load(query, loads)

        result = await self.session.execute(query)
        obj = result.scalar_one_or_none()

        if obj is None:
            name = Booking.__name__
            exception = exception or exceptions.Http404(f"{name} not found.")
            raise exception

        return obj

    async def filter_one(
        self,
        loads: list[LoadType] | None = None,
        **filter_params: Any,
    ) -> Booking | None:
        """Get a record by filters."""

        query = sa.select(Booking)

        for key, value in filter_params.items():
            if not hasattr(Booking, key):
                raise ValueError(
                    f"Model '{Booking.__name__}' does not have attr: '{key}'"
                )

            query = query.where(getattr(Booking, key) == value)

        query = query.limit(1)

        if loads:
            query = self._eager_load(query, loads)

        results = await self.session.execute(query)
        return results.scalar_one_or_none()

    async def count_booked_seats_during_time(
        self,
        restaurant_id: UUID,
        booking_time: datetime.datetime,
        reservation_time_hr: int,
    ) -> int:
        """Count the number of booked seats during a time."""

        dt = timedelta(hours=reservation_time_hr)
        target_start_time = booking_time
        target_end_time = booking_time + dt

        query = sa.select(sa.func.sum(Booking.number_of_people)).filter(
            Booking.restaurant_id == restaurant_id,
            Booking.booking_time < target_end_time,
            Booking.booking_time + dt > target_start_time,
            sa.or_(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.status == BookingStatus.PENDING,
            ),
        )

        result = await self.session.execute(query)
        total_people = result.scalar() or 0
        return total_people

    async def check_duplicate_booking(
        self,
        email: str,
        restaurant_id: UUID,
        booking_time: datetime.datetime,
        reservation_time_hr: int,
    ) -> bool:
        """Check if a booking exists for the email in the last n hours."""

        dt = timedelta(hours=reservation_time_hr)
        end_time = booking_time + dt

        query = sa.select(Booking).filter(
            Booking.email == email,
            Booking.restaurant_id == restaurant_id,
            sa.and_(
                Booking.booking_time < end_time,
                Booking.booking_time + dt > booking_time,
            ),
            sa.or_(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.status == BookingStatus.PENDING,
            ),
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    # async def get_offset_results(
    #     self,
    #     out_dto: Type[OutputDTO],
    #     pagination: PaginationType,
    #     query: sa.sql.Select[tuple[Model]] | None = None,
    # ) -> OffsetResults[OutputDTO]:
    #     """Get offset paginated records."""

    #     if query is None:
    #         query = sa.select(Booking)

    #     query = query.offset(pagination.offset).limit(pagination.limit)
    #     results = await self.session.execute(query)

    #     return OffsetResults(
    #         data=[out_dto.model_validate(row) for row in results.scalars()],
    #     )

    @staticmethod
    def _eager_load(
        query: sa.sql.Select[tuple[Model]],
        loads: list[LoadType],
    ) -> sa.sql.Select[tuple[Model]]:
        """Eager load items to query."""

        for load in loads:
            if isinstance(load, orm.InstrumentedAttribute):
                query = query.options(orm.joinedload(load))
            else:
                query = query.options(load)

        return query


class BookingWriteDAO:
    """Class for accessing Booking table WRITE."""

    def __init__(self, session: GetDBSession):
        self.session = session

    async def create(
        self,
        input_dto: BookingInputDTO,
        id: UUID | None = None,
    ) -> UUID:
        """Create a record."""

        if id is None:
            id = uuid4()

        base = Booking(id=id, **input_dto.model_dump())
        self.session.add(base)
        await self.session.flush()
        return id

    async def update(
        self,
        id: UUID,
        update_dto: BookingUpdateDTO,
    ) -> None:
        """Update a record."""

        query = (
            sa.update(Booking)
            .where(Booking.id == id)
            .values(
                **update_dto.model_dump(),
            )
        )

        await self.session.execute(query)
        await self.session.flush()


GetDAORO = Annotated[BookingReadDAO, Depends(BookingReadDAO)]
GetDAO = Annotated[BookingWriteDAO, Depends(BookingWriteDAO)]
