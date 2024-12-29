from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID

from pydantic import Field, SecretStr


# Base
class BaseOrmModel(BaseModel):
    """BaseOrmModel."""

    model_config = ConfigDict(from_attributes=True)


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


#############
# Core DTOs #
#############


class _BaseUserBaseDTO(BaseOrmModel):
    """Base DTO for user."""

    id: UUID
    email: str
    created_at: datetime


class BaseUserDTO(_BaseUserBaseDTO):
    """DTO for user."""


class BaseUserInputDTO(BaseModel):
    """DTO for creating a user."""

    email: str
    password: str


#############
# Auth DTOs #
#############


class TokenData(BaseModel):
    """Token data."""

    user_id: UUID


class UserLoginDTO(BaseModel):
    """DTO for user login."""

    email: str
    password: SecretStr


class UserCreateDTO(BaseModel):
    """DTO for user creation."""

    email: str
    password: SecretStr


class LoginResponse(BaseModel):
    """Response model for login."""

    access_token: str
