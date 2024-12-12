import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, computed_field


class BaseOrmModel(BaseModel):
    """BaseOrmModel."""

    model_config = ConfigDict(from_attributes=True)
