from pydantic import BaseModel, ConfigDict


class UserRequestDTO(BaseModel):
    user_input: str


class RestaurantInputDTO(BaseModel):
    restaurant_id: str
    description: str


class RestaurantModelDTO(RestaurantInputDTO):
    model_config = ConfigDict(from_attributes=True)


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
                f"- {restaurant.restaurant_id} - {restaurant.description}"
                for restaurant in self.restaurants
            ]
        )
        return (
            f"You are tasked with helping a user select a restaurant based on their query. "
            f"Here is a list of available restaurants:\n{restaurant_list}\n\n"
            f"The user asks: {self.user_input}"
            f"PLease respond in a joyful matter as if you were a waiter: {self.user_input}"
        )
