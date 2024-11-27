from fastapi import APIRouter, Depends
from api.dtos.chat_dtos import UserPrompt, UserRequestDTO
from db.dependencies import get_db_session
from services.chat import make_chat
from sqlalchemy.ext.asyncio import AsyncSession

from services.embeddings import search_embedding

router = APIRouter()


@router.post("/chat")
async def chat(
    input_dto: UserRequestDTO, session: AsyncSession = Depends(get_db_session)
):
    result = await search_embedding(input_dto=input_dto, session=session)
    prompt = UserPrompt(user_input=input_dto.user_input, restaurants=result)
    

    response = await make_chat(prompt)
    return {"data": response}
