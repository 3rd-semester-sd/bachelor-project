from fastapi import APIRouter, Request
from typing import Any


router = APIRouter()


@router.get("/health")
async def health_check() -> bool:
    """Return True if the service is healthy."""
    return True


@router.get("/jwt-test")
async def test_jwt(request: Request) -> Any:
    """Return True if the service is healthy."""
    return dict(request.headers)
