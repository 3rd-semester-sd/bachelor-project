from pydantic_settings import BaseSettings, SettingsConfigDict

PREFIX = "BOOKING_SERVICE_"


class Settings(BaseSettings):
    """Settings for the booking service."""

    host: str = "localhost"
    port: int = 8000
    log_level: str = "info"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=PREFIX,
    )


settings = Settings()
