from uuid import UUID

import sqlalchemy as sa


from daos import BaseDAORO, BaseDAOWO
from dtos import BookingInputDTO
from models import Booking


class BookingReadDAO(BaseDAORO[Booking]):
    """Class for accessing Booking table READ."""


class BookingWriteDAO(BaseDAOWO[Booking, BookingInputDTO]):
    """Class for accessing Booking table WRITE."""
