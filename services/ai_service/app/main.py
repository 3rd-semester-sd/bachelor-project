import asyncio
from typing import Any
from fastapi import FastAPI
from prometheus_client import make_asgi_app  # type: ignore
from contextlib import asynccontextmanager
from app.api.routes.chat import router as chat_router
from app.api.routes.embedding import router as embedding_router
from app.lifespan import setup_es
from app.services.rabbit.lifetime import init_rabbit, shutdown_rabbit
from app.services.azure_ai.client import get_embedding_client
from app.services.rabbit.dependencies import RMQService
from app.services.es.dependencies import ElasticsearchService
from app.services.prometheus.prometheus import (
    MetricsMiddleware,
)

metrics_app = make_asgi_app()  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize metrics middleware
    metrics = MetricsMiddleware(app)
    app.state.metrics = metrics

    try:
        # Setup ES
        await setup_es(app=app)
        metrics.update_dependency_health("elasticsearch", True)

        # Initialize RabbitMQ
        init_rabbit(app)
        metrics.update_dependency_health("rabbitmq", True)

        # Setup AI client
        ai_client = get_embedding_client()
        metrics.update_dependency_health("azure_ai", True)

        es_service = ElasticsearchService(es_client=app.state.es)

        # Start consuming messages
        rmq_service = RMQService(
            pool=app.state.rmq_channel_pool, ai_client=ai_client, es_service=es_service
        )

        # Create periodic task to update system metrics every n secs
        async def periodic_metrics_update():
            while True:
                metrics.update_system_metrics()
                await asyncio.sleep(15)  

        metrics_task = asyncio.create_task(periodic_metrics_update())
        consume_task = asyncio.create_task(rmq_service.declare_and_consume())

        yield

        # Cleanup
        metrics_task.cancel()
        consume_task.cancel()
        await shutdown_rabbit(app)

        try:
            await consume_task
        except asyncio.CancelledError:
            pass

    except Exception as e:
        metrics.track_error(type(e).__name__, "lifespan")
        raise


app = FastAPI(lifespan=lifespan, root_path="/ai-service")


@app.get("/api/health")
async def health() -> dict[str, Any]:
    metrics = app.state.metrics

    async with metrics.track_async_operation("health_check"):
        health_status: dict[str, Any] = {
            "status": "ok",
            "version": "0.0.1",
            "services": {
                "rabbitmq": "connected",
                "elasticsearch": "connected",
                "azure_ai": "connected",
            },
        }
        return health_status


# Add middleware before including routers
app.add_middleware(MetricsMiddleware)

# Mount metrics endpoint
app.mount("/metrics", metrics_app)  # type: ignore

# Include routers
app.include_router(prefix="/api", router=chat_router)
app.include_router(prefix="/api", router=embedding_router)
