from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncAzureOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dtos.chat_dtos import RestaurantEmbeddingInputDTO, RestaurantInputDTO
from app.db.dependencies import get_db_session
from app.services.client import get_embedding_client
from app.services.embeddings import generate_restaurant_embedding, save_embedding

router = APIRouter()


@router.post("/embedding")
async def add_embedding(
    input_dto: RestaurantInputDTO,
    session: AsyncSession = Depends(get_db_session),
    embedding_client: AsyncAzureOpenAI = Depends(get_embedding_client),
) -> dict[str, RestaurantEmbeddingInputDTO]:
    """Endpoint to generate and save an embedding for a restaurant."""
    try:
        embedding = await generate_restaurant_embedding(
            input_dto=input_dto, client=embedding_client
        )
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
