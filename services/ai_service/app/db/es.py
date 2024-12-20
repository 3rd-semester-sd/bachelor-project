from elasticsearch import AsyncElasticsearch
from app.settings import settings

es_client = AsyncElasticsearch(hosts=[settings.ai_elasticsearch_url])


# Function to ensure the Elasticsearch index exists with appropriate mappings
async def ensure_es_index():
    index_name = "restaurants"
    exists = await es_client.indices.exists(index=index_name)
    if not exists:
        await es_client.indices.create(
            index=index_name,
            body={
                "mappings": {
                    "properties": {
                        "restaurant_id": {"type": "keyword"},
                        "restaurant_name": {"type": "text"},
                        "restaurant_description": {"type": "text"},
                        "restaurant_address": {"type": "text"},
                        "restaurant_location": {"type": "text"},
                        "cuisine_type": {"type": "keyword"},
                    }
                }
            },
        )


async def update_restaurant(
    es_client: AsyncElasticsearch,
    restaurant_id: str,
    embedding: list[float],
) -> None:
    doc = {"embedding": embedding}
    await es_client.update(index="restaurant", id=restaurant_id, body={"doc": doc})
