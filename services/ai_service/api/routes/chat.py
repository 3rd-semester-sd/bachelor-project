from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from api.dtos.chat_dtos import RestaurantModelDTO, UserPrompt, UserRequestDTO
from db.dependencies import get_db_session
from services.chat import make_chat
from sqlalchemy.ext.asyncio import AsyncSession

from services.embeddings import search_embedding

router = APIRouter()


@router.post("/chat")
async def chat_with_embeddings(
    input_dto: UserRequestDTO, session: AsyncSession = Depends(get_db_session)
) -> dict[str, Any]:
    """Endpoint to generate a response based on user input and embeddings."""
    try:
        result = await search_embedding(input_dto=input_dto, session=session)

        if not result:
            raise HTTPException(status_code=404, detail="No embeddings found.")
        
        prompt = UserPrompt(user_input=input_dto.user_input, restaurants=result)
        response = await make_chat(prompt)
        
        return {"data": response.choices[0].message.content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
