from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from app.settings import settings


async def setup_es(app: FastAPI) -> None:
    """Setup Elasticsearch."""
    es_client = AsyncElasticsearch(
        hosts=[settings.ai_elasticsearch_url],
        # api_key=
    )
    await es_client.info()
    app.state.es = es_client
