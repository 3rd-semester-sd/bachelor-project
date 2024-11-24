from pydantic import BaseModel


class UserRequestDTO(BaseModel):
    user_input: str


class UserPrompt(BaseModel):
    prompt: str
