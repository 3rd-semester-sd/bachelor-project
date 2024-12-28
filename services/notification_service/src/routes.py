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


@base_router.get("/ready")
async def readiness_check(request: Request) -> bool:
    """Return True if the service is ready."""
    logger.info(f"Request: {request.headers}")
    return True
