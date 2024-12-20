from openai import AsyncAzureOpenAI
from app.api.dtos.chat_dtos import (
    RestaurantEmbeddingInputDTO,
    RestaurantInputDTO,
    RestaurantModelDTO,
    UserRequestDTO,
)

from app.settings import settings
import logging
from app.db.dependencies import ElasticsearchService, GetES


logger = logging.getLogger(__name__)


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
        restaurant_id=input_dto.restaurant_id,
        description=input_dto.description,
        embedding=embedding,
    )


async def search_embedding(
    input_dto: UserRequestDTO,
    client: AsyncAzureOpenAI,
    model: str = settings.ai_embedding_azure_model,
    limit: int = 2,
) -> list[RestaurantModelDTO] | None:
    """Search embedding using similarity search."""
    embedding = await _generate_embedding(
        input_dto.user_input, client=client, model=model
    )
    if embedding is None:
        logger.warning("Failed to generate user embedding for search.")
        return None

    return None
    return (
        [RestaurantModelDTO.model_validate(restaurant) for restaurant in result]
        if result
        else None
    )
