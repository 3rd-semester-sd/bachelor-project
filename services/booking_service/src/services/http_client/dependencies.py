from httpx import AsyncClient
from typing import Annotated, Any, AsyncGenerator
from fastapi import Depends

import exceptions
from settings import settings
from uuid import UUID
from pydantic import BaseModel
from fastapi import Request


async def get_http_client(request: Request) -> AsyncGenerator[AsyncClient, None]:
    """Get an HTTP client."""
    yield request.app.state.http_client


GetHTTPClient = Annotated[AsyncClient, Depends(get_http_client)]


class RestaurantSettingsDTO(BaseModel):
    """Restaurant settings DTO."""

    max_seats: int
    opening_hr: int
    closing_hr: int
    open_days: list[int]  # (1, 1, 1, 1, 1, 1, 0)
    reservation_time_hr: int
    closing_time_buffer_hr: int


class RestaurantResponseDTO(BaseModel):
    """Restaurant response DTO."""

    restaurant_id: UUID
    restaurant_name: str
    restaurant_settings: RestaurantSettingsDTO


class HttpClient:
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

        json = None
        try:
            json = response.json()
        except Exception as e:
            raise exceptions.Http500(f"Failed to parse response: {e}")

        if json is None:
            raise exceptions.Http500("Failed to parse response: no data")

        if response.status_code != 200:
            raise exceptions.Http500(
                f"Failed to make request: {json.get('error', 'No error message')}"
            )

        return json

    async def get_restaurant_by_id(
        self,
        restaurant_id: UUID,
    ) -> RestaurantResponseDTO:
        """Get a restaurant by ID."""

        response_json = await self._base_request(
            method="GET",
            url=f"{settings.restaurant_service_url}/api/restaurants/{restaurant_id}",
        )

        if "data" not in response_json:
            raise exceptions.Http500("Invalid response format")

        return RestaurantResponseDTO.model_validate(response_json["data"])

    async def verify_membership(
        self,
        user_id: UUID,
        restaurant_id: UUID,
    ) -> None:
        """Verify that a user is a member of a restaurant."""

        response_json = await self._base_request(
            method="GET",
            url=f"{settings.restaurant_service_url}/api/restaurants"
            f"/{restaurant_id}/members/{user_id}",
        )

        if "data" not in response_json:
            raise exceptions.Http500("Invalid response format")

        if response_json["data"] is False:
            raise exceptions.Http403("User is not a member of the restaurant")


GetRestaurantClient = Annotated[HttpClient, Depends()]
