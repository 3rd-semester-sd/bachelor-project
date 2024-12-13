import json
import requests
from pydantic import BaseModel

class RestaurantInputDTO(BaseModel):
    name: str
    description: str


with open("services/ai_service/test_data/restaurants.json") as f:
    data = json.load(f)
    restaurants = [RestaurantInputDTO(**input_data) for input_data in data]


# add to db by using endpoint
for restaurant in restaurants:
    requests.post(url="http://localhost:8089/embedding", json=restaurant.model_dump())
