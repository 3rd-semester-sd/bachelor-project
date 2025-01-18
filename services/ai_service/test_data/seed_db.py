import json
import requests
from pydantic import BaseModel, Field
from faker import Faker
import random
from typing import Any, List


fake = Faker()
CUISINE_TYPES = [
    "italian",
    "mexican",
    "japanese",
    "indian",
]


class RestaurantInputDTO(BaseModel):
    name: str
    description: str


class RestaurantSettings(BaseModel):
    max_seats: int = Field(default=30)
    opening_hr: int = Field(default=10)
    closing_hr: int = Field(default=22)
    open_days: list[int] = Field(default=[1, 1, 1, 1, 1, 1, 0])
    reservation_time_hr: int = Field(default=2)
    closing_time_buffer_hr: int = Field(default=2)


class RestaurantPostDTO(BaseModel):
    restaurant_name: str = Field(..., alias="restaurant_name")
    restaurant_description: str = Field(..., alias="restaurant_description")
    restaurant_address: str = Field(..., alias="restaurant_address")
    restaurant_location: str = Field(..., alias="restaurant_location")
    cuisine_type: str = Field(..., alias="cuisine_type")
    restaurant_settings: RestaurantSettings = Field(default=RestaurantSettings())


def load_restaurants_from_json(file_path: str) -> List[RestaurantInputDTO]:
    """
    Load restaurant data from a JSON file and parse it into RestaurantInputDTO instances.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        restaurants = [RestaurantInputDTO(**item) for item in data]
    return restaurants


def generate_additional_fields() -> dict[str, Any]:
    """
    Generate additional required fields using Faker and random selection.
    """
    address = fake.address().replace(
        "\n", ", "
    )  # Replace newlines with commas for consistency
    location = fake.city()
    cuisine_type = random.choice(CUISINE_TYPES)
    return {
        "restaurant_address": address,
        "restaurant_location": location,
        "cuisine_type": cuisine_type,
    }


def post_restaurant(restaurant_data: RestaurantPostDTO, url: str) -> None:
    """
    Send a POST request to the specified URL with the restaurant data.
    Returns True if the request was successful, else False.
    """
    try:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZmMwMTVhYzEtOGMxZi00MzY1LWE1NzctMDliMDQzNDNjNzk3IiwiZXhwIjoxNzM3MjA2ODY1fQ.5c2d-QGjXXhanKvzcd99Ez9VuXTqRehCQDu6Gyfcaic"
        response = requests.post(
            url=url,
            json=restaurant_data.model_dump(),
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        print(f"Successfully posted restaurant: {restaurant_data.restaurant_name}")
    except Exception as err:
        print(
            f"An error occurred while posting {restaurant_data.restaurant_name}: {err}"
        )


def main():
    json_file_path = "./test_data/restaurants.json"
    restaurants = load_restaurants_from_json(json_file_path)

    endpoint_url = "http://localhost:8080/restaurant-service/api/protected/restaurants"

    for restaurant_input in restaurants:
        # Generate additional fields
        additional_fields = generate_additional_fields()

        restaurant_post = RestaurantPostDTO(
            restaurant_name=restaurant_input.name,
            restaurant_description=restaurant_input.description,
            restaurant_address=additional_fields["restaurant_address"],
            restaurant_location=additional_fields["restaurant_location"],
            cuisine_type=additional_fields["cuisine_type"],
        )

        # Post to the endpoint
        post_restaurant(restaurant_post, endpoint_url)


if __name__ == "__main__":
    main()
