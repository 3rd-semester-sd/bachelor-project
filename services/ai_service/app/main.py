import asyncio
from fastapi import FastAPI
from app.api.routes.chat import router as chat_router
from app.api.routes.embedding import router as embedding_router
from contextlib import asynccontextmanager

from app.lifespan import setup_es
from app.services.rabbit.lifetime import init_rabbit, shutdown_rabbit
from app.services.azure_ai.client import get_embedding_client
from app.services.rabbit.dependencies import RMQService
from app.services.es.dependencies import ElasticsearchService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # setup es
    await setup_es(app=app)
    init_rabbit(app)

    ai_client = get_embedding_client()
    es_service = ElasticsearchService(es_client=app.state.es)

    # start consuming messages from rabbit
    rmq_service = RMQService(
        pool=app.state.rmq_channel_pool, ai_client=ai_client, es_service=es_service
    )
    consume_task = asyncio.create_task(rmq_service.declare_and_consume())

    yield
    #
    consume_task.cancel()  # cancel the consumer task
    await shutdown_rabbit(app)  # close RabbitMQ connections
    try:
        await consume_task  # Wait for the task to finish
    except asyncio.CancelledError:
        pass  # Task was cancelled


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return "ok"


app.include_router(router=chat_router)
app.include_router(router=embedding_router)
