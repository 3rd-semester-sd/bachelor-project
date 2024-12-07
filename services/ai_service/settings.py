from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Base settings."""

    database_url: str = "postgresql+asyncpg://ai:ai@localhost/pg-ai-service"
    openai_azure_key: str = ""
    openai_azure_endpoint: str = ""

    embedding_azure_key: str = ""
    embedding_azure_endpoint: str = ""
    embedding_azure_model: str = "text-embedding-ada-002"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
