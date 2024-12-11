from fastapi import FastAPI
from app.api.routes.chat import router as chat_router
from app.api.routes.embedding import router as embedding_router
from contextlib import asynccontextmanager

from app.lifespan import setup_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    await setup_db(app=app)
    yield
    await app.state.db_engine.dispose()


app = FastAPI(lifespan=lifespan)


app.include_router(router=chat_router)
app.include_router(router=embedding_router)
