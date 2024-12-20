from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncAzureOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dtos.chat_dtos import RestaurantModelDTO, UserPrompt, UserRequestDTO
from app.services.chat import generate_chat_response
from app.services.client import get_chat_client, get_embedding_client
from app.services.embeddings import search_embedding

router = APIRouter()


@router.post("/chat")
async def chat_with_embeddings(
    input_dto: UserRequestDTO,
    chat_client: AsyncAzureOpenAI = Depends(get_chat_client),
    embedding_client: AsyncAzureOpenAI = Depends(get_embedding_client),
) -> dict[str, Any]:
    """Endpoint for generating a response based on user input and embeddings."""
    try:
        result = await search_embedding(input_dto=input_dto, client=embedding_client)

        if not result:
            raise HTTPException(status_code=404, detail="No embeddings found.")

        prompt = UserPrompt(user_input=input_dto.user_input, restaurants=result)
        response = await generate_chat_response(prompt=prompt, client=chat_client)

        return {"data": response}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
