from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Type, TypeVar
import dtos
import jwt
from pydantic import ValidationError
import json
from uuid import UUID
import exceptions
from settings import settings
from passlib.context import CryptContext
import daos
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer as _HTTPBearer

from uuid import UUID

ALGORITHM = "HS256"

CREATE_TOKEN_EXPIRE_MINUTES = 30


class Encoder(json.JSONEncoder):
    def default(self, obj: Any):
        if isinstance(obj, UUID):
            return str(obj)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password."""
    return pwd_context.verify(plain_password, hashed_password)


def _encode_token(data: dtos.TokenData, expires_at: datetime) -> str:
    """Encode a token."""

    to_encode = data.model_dump()
    to_encode["exp"] = expires_at

    return jwt.encode(
        to_encode,
        settings.jwt_secret.get_secret_value(),
        algorithm=ALGORITHM,
        json_encoder=Encoder,
    )


def create_access_token(data: dtos.TokenData) -> str:
    """Create an access token."""

    return _encode_token(
        data,
        datetime.now(timezone.utc)
        + timedelta(
            minutes=CREATE_TOKEN_EXPIRE_MINUTES,
        ),
    )


def decode_token(token: str) -> dtos.TokenData:
    """Decode a token, returning the payload."""

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[ALGORITHM],
        )
        return dtos.TokenData(**payload)

    except jwt.exceptions.PyJWTError:
        raise exceptions.Http401(detail="Invalid token")


class HTTPBearer(_HTTPBearer):
    """
    HTTPBearer with access token.
    Returns access token as str.
    """

    async def __call__(self, request: Request) -> str | None:  # type: ignore
        """Return access token."""
        try:
            obj = await super().__call__(request)
            return obj.credentials if obj else None
        except HTTPException:
            raise exceptions.Http401("Missing token.")


auth_scheme = HTTPBearer()


def get_token(token: str = Depends(auth_scheme)) -> str:
    """Return access token as str."""
    return token


GetToken = Annotated[str, Depends(get_token)]


async def get_current_user(
    token: GetToken,
    r_daos: daos.GetDAORO,
) -> dtos.BaseUserDTO:
    """Get current user from token data."""
    token_data = decode_token(token)

    user = await r_daos.filter_one(id=token_data.user_id)

    if not user:
        raise exceptions.Http404("Decoded user not found.")

    return dtos.BaseUserDTO.model_validate(user)


GetCurrentUser = Annotated[dtos.BaseUserDTO, Depends(get_current_user)]
