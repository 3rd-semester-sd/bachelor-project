from httpx import AsyncClient
from fastapi import FastAPI


async def init_http_client(app: FastAPI) -> None:
    """Initialize HTTP client."""

    app.state.http_client = AsyncClient()


async def shutdown_http_client(app: FastAPI) -> None:
    """Shutdown HTTP client."""

    client: AsyncClient = app.state.http_client
    await client.aclose()
