from fastapi import APIRouter
from .health_routes import router as health_router


base_router = APIRouter()


base_router.include_router(health_router)
