import json

from pydantic import BaseModel
import requests


class RestaurantInputDTO(BaseModel):
    name: str
    description: str


with open("test_data/restaurants.json") as f:
    # Read the file and parse JSON
    data = json.load(f)  # Parse JSON directly into a Python object

    # Convert each item into a RestaurantInputDTO
    dtos = [RestaurantInputDTO(**input_data) for input_data in data]

# Debug print to verify the conversion
for dto in dtos:
    requests.post(url="http://localhost:8000/embedding", json=dto.model_dump())
