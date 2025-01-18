from openai import AsyncAzureOpenAI
from app.api.dtos.dtos import (
    RestaurantEmbeddingInputDTO,
    RestaurantInputDTO,
    UserRequestDTO,
)

from app.settings import settings
from loguru import logger
from app.services.es.dependencies import ElasticsearchService, GetES


async def _generate_embedding(
    input_str: str,
    client: AsyncAzureOpenAI,
    model: str,
) -> list[float] | None:
    """Generate embedding for a given input string."""

    response = await client.embeddings.create(input=[input_str], model=model)
    if response and response.data:
        return response.data[0].embedding
    logger.warning(
        f"No embedding generated for input: '{input_str}'. Response was empty."
    )
    return None


async def generate_restaurant_embedding(
    input_dto: RestaurantInputDTO,
    ai_client: AsyncAzureOpenAI,
    es_client: ElasticsearchService,
    model: str = settings.ai_embedding_azure_model,
) -> RestaurantEmbeddingInputDTO | None:
    """Generate restaurant embedding and return as DTO."""

    embedding = await _generate_embedding(
        input_dto.description, client=ai_client, model=model
    )

    if embedding is None:
        logger.warning(
            f"Failed to generate embedding for restaurant: {input_dto.restaurant_id}"
        )
        return None

    await es_client.update_restaurant(
        restaurant_id=input_dto.restaurant_id, embedding=embedding
    )

    return RestaurantEmbeddingInputDTO(
        **input_dto.model_dump(),
        embedding=embedding,
    )


async def search_embedding(
    input_dto: UserRequestDTO,
    client: AsyncAzureOpenAI,
    es_service: ElasticsearchService,
    limit: int,
    model: str = settings.ai_embedding_azure_model,
) -> list[RestaurantInputDTO] | None:
    """Search embedding using similarity search."""

    embedding = await _generate_embedding(
        input_dto.user_input, client=client, model=model
    )

    if embedding is None:
        logger.warning("Failed to generate user embedding for search.")
        return None

    if len(embedding) != 3072:
        logger.error(
            f"Embedding dimension mismatch: Expected 3072, got {len(embedding)}"
        )

    result = await es_service.similarity_search(embedding=embedding, limit=limit)

    return (
        [
            RestaurantInputDTO(
                restaurant_id=restaurant["_id"],
                description=restaurant["_source"]["restaurant_description"],
                restaurant_name=restaurant["_source"]["restaurant_name"],
            )
            for restaurant in result
        ]
        if result
        else None
    )
