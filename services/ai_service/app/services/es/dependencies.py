from typing import Annotated, Any
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, Request
import logging


def get_es_client(request: Request) -> AsyncElasticsearch:
    """Get Elasticsearch client from app state."""
    return request.app.state.es


logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Elasticsearch Service."""

    def __init__(
        self,
        es_client: AsyncElasticsearch = Depends(get_es_client),
    ) -> None:
        self.es_client = es_client

    async def get_info(self):
        mapping = await self.es_client.indices.get_mapping(index="restaurants")
        print(mapping)

    async def update_restaurant(
        self,
        restaurant_id: str,
        embedding: list[float],
    ) -> None:
        doc = {"embedding": embedding}
        await self.es_client.update(
            index="restaurants", id=restaurant_id, body={"doc": doc}
        )

    async def similarity_search(self, embedding: list[float], limit: int = 1):
        """Performs a similarity seach using elastic search."""

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
        
        print(len(hits), "hiiiits")
        # Extract the source documents from hits
        return [hit for hit in hits]


GetES = Annotated[ElasticsearchService, Depends(ElasticsearchService)]
