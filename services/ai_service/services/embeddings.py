from openai import AsyncAzureOpenAI
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from api.dtos.chat_dtos import (
    RestaurantEmbeddingInputDTO,
    RestaurantInputDTO,
    RestaurantModelDTO,
    UserRequestDTO,
)
from db.models import RestaurantDataModel
from services.client import embedding_client
from settings import settings
import logging

logger = logging.getLogger(__name__)


async def save_embedding(
    embedding_input: RestaurantEmbeddingInputDTO, session: AsyncSession
) -> None:
    """Save embedding to the database."""
    try:
        query = insert(RestaurantDataModel).values(embedding_input.model_dump())
        await session.execute(query)
    except Exception as e:
        logger.error(f"Error saving embedding: {e}")
        raise


async def _generate_embedding(
    input_str: str,
    client: AsyncAzureOpenAI,
    model: str,
) -> list[float]:
    """Generate embedding for a given input string."""
    try:
        response = await client.embeddings.create(input=[input_str], model=model)
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding for input '{input_str}': {e}")
        raise


async def generate_restaurant_embedding(
    input_dto: RestaurantInputDTO,
    client: AsyncAzureOpenAI = embedding_client,
    model: str = settings.embedding_azure_model,
) -> RestaurantEmbeddingInputDTO:
    """Generate restaurant embedding and return as DTO."""
    embedding = await _generate_embedding(
        input_dto.description, client=client, model=model
    )
    return RestaurantEmbeddingInputDTO(
        name=input_dto.name,
        description=input_dto.description,
        embedding=embedding,
    )


async def search_embedding(
    input_dto: UserRequestDTO,
    session: AsyncSession,
    client: AsyncAzureOpenAI = embedding_client,
    model: str = settings.embedding_azure_model,
) -> list[RestaurantModelDTO]:
    """Search for the nearest embeddings."""
    embedding = await _generate_embedding(
        input_dto.user_input, client=client, model=model
    )
    query = (
        select(RestaurantDataModel)
        .order_by(RestaurantDataModel.embedding.l2_distance(embedding))
        .limit(2)
    )
    try:
        result = await session.scalars(query)
        return [RestaurantModelDTO.model_validate(restaurant) for restaurant in result]
    except Exception as e:
        logger.error(f"Error searching embedding: {e}")
        raise
