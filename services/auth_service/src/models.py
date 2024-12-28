import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class BaseUser(Base):
    """Base user model."""

    __tablename__ = "base_user"

    email: Mapped[str] = mapped_column(
        sa.String,
        nullable=False,
        unique=True,
    )
    password: Mapped[str] = mapped_column(
        sa.String,
        nullable=False,
    )
