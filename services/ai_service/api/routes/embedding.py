from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.dtos.chat_dtos import RestaurantInputDTO
from db.dependencies import get_db_session
from services.embeddings import generate_restaurant_embedding, save_embedding

router = APIRouter()


@router.post("/embedding")
async def chat(
    input_dto: RestaurantInputDTO, session: AsyncSession = Depends(get_db_session)
):
    embedding = await generate_restaurant_embedding(input_dto=input_dto)

    await save_embedding(embedding_input=embedding, session=session)

    return embedding
