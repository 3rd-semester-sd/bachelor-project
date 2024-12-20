from typing import Annotated
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, Request


def get_es_client(request: Request) -> AsyncElasticsearch:
    """Get Elasticsearch client from app state."""
    return request.app.state.es


class ElasticsearchService:
    """Elasticsearch Service."""

    def __init__(
        self,
        es_client: AsyncElasticsearch = Depends(get_es_client),
    ) -> None:
        self.es_client = es_client

    async def update_restaurant(
        self,
        restaurant_id: str,
        embedding: list[float],
    ) -> None:
        doc = {"embedding": embedding}
        await self.es_client.update(
            index="restaurants", id=restaurant_id, body={"doc": doc}
        )


GetES = Annotated[ElasticsearchService, Depends(ElasticsearchService)]
