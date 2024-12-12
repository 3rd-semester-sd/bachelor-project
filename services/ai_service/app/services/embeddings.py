from openai import AsyncAzureOpenAI
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dtos.chat_dtos import (
    RestaurantEmbeddingInputDTO,
    RestaurantInputDTO,
    RestaurantModelDTO,
    UserRequestDTO,
)
from app.db.models import RestaurantDataModel
from app.settings import settings
import logging

from utils.decorators import handle_db_errors

logger = logging.getLogger(__name__)


@handle_db_errors
async def save_embedding(
    embedding_input: RestaurantEmbeddingInputDTO, session: AsyncSession
) -> None:
    """Save embedding to the database."""

    query = insert(RestaurantDataModel).values(embedding_input.model_dump())
    await session.execute(query)


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
    client: AsyncAzureOpenAI,
    model: str = settings.ai_embedding_azure_model,
) -> RestaurantEmbeddingInputDTO | None:
    """Generate restaurant embedding and return as DTO."""

    embedding = await _generate_embedding(
        input_dto.description, client=client, model=model
    )
    if embedding is None:
        logger.warning(f"Failed to generate embedding for restaurant: {input_dto.name}")
        return None

    return RestaurantEmbeddingInputDTO(
        name=input_dto.name,
        description=input_dto.description,
        embedding=embedding,
    )


@handle_db_errors  # TODO: loosing typing
async def search_embedding(
    input_dto: UserRequestDTO,
    session: AsyncSession,
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

    query = (
        select(RestaurantDataModel)
        .order_by(RestaurantDataModel.embedding.l2_distance(embedding))
        .limit(limit)
    )
    result = await session.scalars(query)
    return (
        [RestaurantModelDTO.model_validate(restaurant) for restaurant in result]
        if result
        else None
    )
