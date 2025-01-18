from typing import Annotated, Any
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, Request
from loguru import logger


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
        """Updates a restaurant in elastic search with a given embedding."""

        doc = {"embedding": embedding}
        await self.es_client.update(
            index="restaurants", id=restaurant_id, body={"doc": doc}
        )

    async def similarity_search(self, embedding: list[float], limit: int = 1):
        """Performs a similarity search using elastic search."""

        query: dict[str, Any] = {
            "size": limit,
            "query": {
                "function_score": {
                    "query": {"bool": {"filter": {"exists": {"field": "embedding"}}}},
                    "script_score": {
                        "script": {
                            "source": """
                                cosineSimilarity(params.query_vector, 'embedding') + 1.0
                            """,
                            "params": {"query_vector": embedding},
                        }
                    },
                    "boost_mode": "replace",  # Ensures the script score replaces the query score
                }
            },
            "sort": [{"_score": {"order": "desc"}}],
        }

        # Execute the search query
        response = await self.es_client.search(index="restaurants", body=query)

        # Extract the hits from the response
        hits = response.get("hits", {}).get("hits", [])

        if not hits:
            logger.info("No matching embeddings found in Elasticsearch.")
            return None

        # Extract the source documents from hits
        return [hit for hit in hits]


GetES = Annotated[ElasticsearchService, Depends(ElasticsearchService)]
