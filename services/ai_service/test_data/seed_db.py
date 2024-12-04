import json

from pydantic import BaseModel
import requests


class RestaurantInputDTO(BaseModel):
    name: str
    description: str


with open("services/ai_service/test_data/restaurants.json") as f:
    data = json.load(f)
    dtos = [RestaurantInputDTO(**input_data) for input_data in data]


# add to db by using endpoint
for dto in dtos:
    requests.post(url="http://localhost:8000/embedding", json=dto.model_dump())
