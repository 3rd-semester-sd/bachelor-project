from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.dtos.chat_dtos import RestaurantEmbeddingInputDTO, RestaurantInputDTO
from db.dependencies import get_db_session
from services.embeddings import generate_restaurant_embedding, save_embedding

router = APIRouter()


@router.post("/embedding")
async def add_embedding(
    input_dto: RestaurantInputDTO, session: AsyncSession = Depends(get_db_session)
) -> dict[str, RestaurantEmbeddingInputDTO]:
    """Endpoint to generate and save an embedding for a restaurant."""
    try:

        embedding = await generate_restaurant_embedding(input_dto=input_dto)
        if embedding is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to generate embedding for the provided input.",
            )

        await save_embedding(embedding_input=embedding, session=session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "data": embedding,
    }
