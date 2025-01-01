from httpx import AsyncClient, Response
from typing import Annotated, Any, AsyncGenerator
from fastapi import Depends
import exceptions
from settings import settings
from uuid import UUID
from pydantic import BaseModel


async def get_http_client() -> AsyncGenerator[AsyncClient, None]:
    """Get an HTTP client."""
    async with AsyncClient() as client:
        yield client


GetHTTPClient = Annotated[AsyncClient, Depends(get_http_client)]


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
    ) -> Response:
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

        return response

    async def get_restaurant_by_id(
        self,
        restaurant_id: UUID,
    ) -> Response:
        """Get a restaurant by ID."""
        url = settings.restaurant_service_url + str(restaurant_id)
        return await self._base_request("GET", url)
