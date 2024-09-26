from settings import settings

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from routes import base_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan."""
    yield


def get_application() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(base_router)
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "__init__:get_application",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        lifespan="on",
        reload=True,
        factory=True,
    )
