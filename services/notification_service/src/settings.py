import pathlib
from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings as PydanticBaseSettings
from yarl import URL

PREFIX = "BOOKING_SERVICE_"

DOTENV = pathlib.Path(__file__).parent.parent / ".env"


class BaseSettings(PydanticBaseSettings):
    """Base settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    def __repr__(self) -> str:
        """Return settings as a string."""
        return f"{self.__class__.__name__}({self.model_dump()})"


class Settings(BaseSettings):
    """Settings for the booking service."""

    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    log_level: str = "info"
    reload: bool = False

    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_prefix=PREFIX,
    )


settings = Settings()
