import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector  # type: ignore


class Base(DeclarativeBase):
    """Base model for all other models."""

    metadata = sa.MetaData()

    __tablename__: str

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )


class RestaurantData(Base):
    """Restaurant model."""

    __tablename__ = "server"

    name: Mapped[str] = mapped_column(sa.String(255))
    description: Mapped[str] = mapped_column(sa.String(255))
    embedding = mapped_column(Vector(3))
