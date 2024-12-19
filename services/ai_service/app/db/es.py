from elasticsearch import AsyncElasticsearch
from app.settings import settings

es_client = AsyncElasticsearch(hosts=[settings.ELASTICSEARCH_URL])


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
