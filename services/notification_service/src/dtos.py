import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ComputedCreatedAt(BaseModel):
    """ComputedCreatedAt."""

    @computed_field  # type: ignore
    @property
    def created_at(self) -> datetime:
        """Get current datetime."""
        return datetime.now(timezone.utc)


class _BaseNotificationDTO(ComputedCreatedAt):
    """Base model for publishing messages."""
