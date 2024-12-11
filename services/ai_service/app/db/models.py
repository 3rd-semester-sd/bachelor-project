import uuid
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector  # type: ignore

from app.db.meta import meta


class Base(DeclarativeBase):
    """Base model for all other models."""

    metadata = meta

    __tablename__: str

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class RestaurantDataModel(Base):
    """Restaurant model."""

    __tablename__ = "restaurant_data"

    name: Mapped[str] = mapped_column(sa.String(255))
    description: Mapped[str] = mapped_column(sa.String(5000))
    embedding = mapped_column(Vector(3072))
