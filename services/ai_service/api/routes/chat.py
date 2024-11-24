from fastapi import APIRouter, Depends
from db.database import get_session
from services.chat import search_and_generate_response

router = APIRouter()


@router.post("/chat")
async def chat(user_query: str, session=Depends(get_session)):
    response = await search_and_generate_response(user_query, session)
    return {"response": response}
