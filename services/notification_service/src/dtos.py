from datetime import datetime, timezone

from pydantic import BaseModel, computed_field


class ComputedCreatedAt(BaseModel):
    """ComputedCreatedAt."""

    @computed_field  # type: ignore
    @property
    def created_at(self) -> datetime:
        """Get current datetime."""
        return datetime.now(timezone.utc)


class EmailDTO(BaseModel):
    """Email data transfer object."""

    email: str
    subject: str
    body: str
    html: str | None = None
