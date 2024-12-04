from openai import AsyncAzureOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from api.dtos.chat_dtos import (
    RestaurantEmbeddingInputDTO,
    RestaurantInputDTO,
    RestaurantModelDTO,
    UserRequestDTO,
)
from db.models import RestaurantDataModel
from services.client import embedding_client


async def save_embedding(
    embedding_input: RestaurantEmbeddingInputDTO, session: AsyncSession
) -> None:
    query = insert(RestaurantDataModel).values(embedding_input.model_dump())

    await session.execute(query)
    await session.commit()


async def _generate_embedding(
    input_str: str,
    client: AsyncAzureOpenAI = embedding_client,
    model: str = "text-embedding-ada-002",
) -> list[float]:
    response = await client.embeddings.create(input=[input_str], model=model)

    embedding = response.data[0].embedding
    return embedding


async def generate_restaurant_embedding(
    input_dto: RestaurantInputDTO,
    client: AsyncAzureOpenAI = embedding_client,
    model: str = "text-embedding-ada-002",
) -> RestaurantEmbeddingInputDTO:
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
    model: str = "text-embedding-ada-002",
) -> list[RestaurantModelDTO]:
    embedding = await _generate_embedding(
        input_dto.user_input, client=client, model=model
    )
    query = (
        select(RestaurantDataModel)
        .order_by(RestaurantDataModel.embedding.l2_distance(embedding))
        .limit(2)
    )
    restaurant_rows = await session.scalars(query)
    restaurants = restaurant_rows.fetchall()
    print(restaurants)

    return [RestaurantModelDTO.model_validate(restaurant) for restaurant in restaurants]
