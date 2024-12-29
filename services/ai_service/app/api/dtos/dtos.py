from datetime import datetime
from pydantic import BaseModel, Field


class UserRequestDTO(BaseModel):
    user_input: str


class RestaurantInputDTO(BaseModel):
    restaurant_id: str
    description: str


class RestaurantRabbitStatusDTO(BaseModel):
    saga_id: str
    time_stamp: datetime = Field(default_factory=datetime.now)
    result: str = "Failed"
    error: str | None = None


class RestaurantRabbitInputDTO(RestaurantInputDTO, RestaurantRabbitStatusDTO): ...


class RestaurantModelDTO(RestaurantInputDTO):
    restaurant_name: str


class RestaurantEmbeddingDTO(RestaurantInputDTO):
    embedding: list[float]


class RestaurantEmbeddingInputDTO(RestaurantInputDTO):
    embedding: list[float]


class RestaurantSearchDTO(RestaurantInputDTO):
    restaurants: list[RestaurantInputDTO]


class UserPrompt(UserRequestDTO):
    restaurants: list[RestaurantModelDTO]

    @property
    def prompt(self):
        # Format restaurant names into a bullet-point list
        restaurant_list = "\n".join(
            [
                f"- {restaurant.restaurant_name} - {restaurant.description.strip()}"
                for restaurant in self.restaurants
            ]
        )
        return (
            f"You are tasked with helping a user select a restaurant based on their query. "
            f"Here is a list of available restaurants:\n{restaurant_list}\n\n"
            f"The user asks: {self.user_input}"
            f"Please respond in a joyful matter as if you were a waiter, but be very concise: {self.user_input}"
        )
