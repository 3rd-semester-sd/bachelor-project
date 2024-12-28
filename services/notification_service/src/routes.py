from fastapi import APIRouter, Request
from loguru import logger


base_router = APIRouter(prefix="/api")


#################
# Health routes #
#################


@base_router.get("/health")
async def health_check() -> bool:
    """Return True if the service is healthy."""
    return True


@base_router.get("/authsvc")
async def test_authsvc(request: Request) -> bool:
    """Test authsvc."""
    logger.info(f"Request: {request.headers}")
    return True
