from fastapi import FastAPI
from api.routes.chat import router
from contextlib import asynccontextmanager

from lifespan import setup_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    await setup_db(app=app)
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(router=router)
