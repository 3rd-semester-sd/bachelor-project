from httpx import AsyncClient
from typing import Annotated, Any, AsyncGenerator
from fastapi import Depends
import exceptions
from settings import settings
from uuid import UUID, uuid4
from pydantic import BaseModel


async def get_http_client() -> AsyncGenerator[AsyncClient, None]:
    """Get an HTTP client."""
    async with AsyncClient() as client:
        yield client


GetHTTPClient = Annotated[AsyncClient, Depends(get_http_client)]


class ResturantSettingsDTO(BaseModel):
    """Restaurant settings DTO."""

    max_seats: int
    opening_hr: int
    closing_hr: int
    open_days: list[int]  # (1, 1, 1, 1, 1, 1, 0)
    reservation_time_hr: int
    closing_time_buffer_hr: int


class RestaurantReponseDTO(BaseModel):
    """Restaurant response DTO."""

    restaurant_id: UUID
    restaurant_name: str
    restaurant_settings: ResturantSettingsDTO


class RestaurantClient:
    """HTTP client."""

    def __init__(self, client: GetHTTPClient) -> None:
        """Initialize."""
        self.client = client

    async def _base_request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make a request."""

        try:
            response = await self.client.request(
                method,
                url,
                headers=headers,
                json=json,
                data=data,
                **kwargs,
            )
        except Exception as e:
            raise exceptions.Http500(f"Failed to make request: {e}")

        data = None
        try:
            data = response.json()
        except Exception as e:
            raise exceptions.Http500(f"Failed to parse response: {e}")

        if data is None:
            raise exceptions.Http500("Failed to parse response: no data")

        return data

    async def get_restaurant_by_id(
        self,
        restaurant_id: UUID,
    ) -> RestaurantReponseDTO:
        """Get a restaurant by ID."""

        data = await self._base_request(
            method="GET",
            url=settings.restaurant_service_url + str(restaurant_id),
        )

        return RestaurantReponseDTO.model_validate(data["data"])


GetRestaurantClient = Annotated[RestaurantClient, Depends()]
