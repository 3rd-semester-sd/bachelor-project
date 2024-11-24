from fastapi import APIRouter, Depends
from api.dtos.chat_dtos import UserPrompt
from services.chat import make_chat

router = APIRouter()


@router.post("/chat")
async def chat(
    user_query: str,
):
    prompt = UserPrompt(prompt=user_query)
    response = await make_chat(prompt)
    return {"data": response.choices[0].message.content}
