from datetime import datetime
from pydantic import BaseModel, Field


class UserRequestDTO(BaseModel):
    """DTO for user request."""

    user_input: str


class RestaurantInputDTO(BaseModel):
    """DTO for restaurant."""

    restaurant_id: str
    description: str
    restaurant_name: str


class RestaurantRabbitStatusDTO(BaseModel):
    """DTO for RabbitMQ status, where result can be set."""

    saga_id: str
    time_stamp: datetime = Field(default_factory=datetime.now)
    result: str = "Failed"
    error: str | None = None


class RestaurantRabbitInputDTO(RestaurantInputDTO, RestaurantRabbitStatusDTO):
    """DTO for the input, used by embedding and rabbitMQ services."""

    ...


class RestaurantEmbeddingDTO(RestaurantInputDTO):
    """DTO for the embedding and restaurant result."""

    embedding: list[float]


class RestaurantEmbeddingInputDTO(RestaurantInputDTO):
    """DTO for embedding result."""

    embedding: list[float]


class RestaurantSearchDTO(RestaurantInputDTO):
    """DTO for a list of restaurant inputs."""

    restaurants: list[RestaurantInputDTO]


class UserPrompt(UserRequestDTO):
    """Model to hold and generate the user prompts."""

    restaurants: list[RestaurantInputDTO]

    @property
    def prompt(self):
        # Format restaurant names and descriptions into a bullet-point list
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
