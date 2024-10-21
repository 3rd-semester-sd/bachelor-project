import pathlib
from pydantic_settings import BaseSettings, SettingsConfigDict

PREFIX = "BOOKING_SERVICE_"

DOTENV = pathlib.Path(__file__).parent.parent / ".env"
print(DOTENV)


class Settings(BaseSettings):
    """Settings for the booking service."""

    host: str = "localhost"
    svc_port: int = 8000
    workers: int = 1
    log_level: str = "info"
    reload: bool = False

    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_prefix=PREFIX,
    )


settings = Settings()
