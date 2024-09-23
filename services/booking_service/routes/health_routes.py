from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
async def health() -> bool:
    """Return True if the service is healthy."""
    return True
