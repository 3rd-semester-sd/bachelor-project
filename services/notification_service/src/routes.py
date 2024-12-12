from fastapi import APIRouter

base_router = APIRouter()


##################
# Booking routes #
##################


booking_router = APIRouter(prefix="/booking")


@booking_router.post("")
async def create_booking() -> None: ...


base_router.include_router(booking_router)


#################
# Health routes #
#################


@base_router.get("/health")
async def health_check() -> bool:
    """Return True if the service is healthy."""
    return True
